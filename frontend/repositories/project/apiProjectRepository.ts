import { Page } from '@/domain/models/page'
import { Project } from '@/domain/models/project/project'
import ApiService from '@/services/api.service'
import { TagItem } from '~/domain/models/tag/tag'
import { Rule } from '~/domain/models/rule/rule'

const sortableFieldList = ['name', 'projectType', 'createdAt', 'author'] as const
type SortableFields = (typeof sortableFieldList)[number]

export class SearchQuery {
  readonly limit: number = 10
  readonly offset: number = 0
  readonly q: string = ''
  readonly sortBy: SortableFields = 'createdAt'
  readonly sortDesc: boolean = false

  constructor(_limit: string, _offset: string, _q?: string, _sortBy?: string, _sortDesc?: string) {
    this.limit = /^\d+$/.test(_limit) ? parseInt(_limit) : 10
    this.offset = /^\d+$/.test(_offset) ? parseInt(_offset) : 0
    this.q = _q || ''
    this.sortBy = (
      _sortBy && sortableFieldList.includes(_sortBy as SortableFields) ? _sortBy : 'createdAt'
    ) as SortableFields
    this.sortDesc = _sortDesc === 'true'
  }
}

export function toModel(item: { [key: string]: any }): Project {
  return new Project(
    item.id,
    item.name || item._name,
    item.description || item._description,
    item.guideline,
    item.project_type || item._projectType,
    item.random_order || item.enableRandomOrder,
    item.collaborative_annotation || item.enableSharingMode,
    item.single_class_classification || item.exclusiveCategories,
    item.allow_overlapping || item.allowOverlappingSpans,
    item.grapheme_mode || item.enableGraphemeMode,
    item.use_relation || item.useRelation,
    item.tags.map((tag: { [key: string]: any }) => new TagItem(tag.id, tag.text, tag.project)),
    item.allow_member_to_create_label_type || item.allowMemberToCreateLabelType,
    item.discrepancy_active || item._discrepancy_active,
    item.discrepancy_percentage || item._discrepancy_percentage,
    item.users || [],
    item.created_at || '',
    item.updated_at || '',
    item.author || '',
    item.is_text_project || false,
    item.perspective_associated || null,
    item.closed || item._closed || false,
    item.version || item._version || 1,
    item.original_project || item._original_project || null,
    item.is_current_version || item._is_current_version || true
  )
}


function toPayload(item: Project): { [key: string]: any } {
  return {
    id: item.id,
    name: item.name,
    description: item.description,
    guideline: item.guideline,
    project_type: item.projectType,
    random_order: item.enableRandomOrder,
    collaborative_annotation: item.enableSharingMode,
    single_class_classification: item.exclusiveCategories,
    allow_overlapping: item.allowOverlappingSpans,
    grapheme_mode: item.enableGraphemeMode,
    use_relation: item.useRelation,
    tags: item.tags,
    allow_member_to_create_label_type: item.allowMemberToCreateLabelType,
    resourcetype: item.resourceType,
    discrepancy_active: item.discrepancy_active,
    discrepancy_percentage: item.discrepancy_percentage,
    perspective_associated: item.perspective_associated,
    closed: item.closed,
    version: item.version,
    original_project: item.original_project,
    is_current_version: item.is_current_version
  }
}

export class APIProjectRepository {
  constructor(private readonly request = ApiService) {}

  async list(query: SearchQuery): Promise<Page<Project>> {
    const fieldMapper = {
      name: 'name',
      createdAt: 'created_at',
      projectType: 'project_type',
      author: 'created_by'
    }
    const sortBy = fieldMapper[query.sortBy]
    const ordering = query.sortDesc ? `-${sortBy}` : `${sortBy}`
    const url = `/projects?limit=${query.limit}&offset=${query.offset}&q=${query.q}&ordering=${ordering}`
    const response = await this.request.get(url)
    
    // Filter to keep only the most recent version of each project
    const projects = response.data.results.map((project: { [key: string]: any }) => toModel(project))
    const latestVersions = new Map<number, Project>()
    
    projects.forEach((project: Project) => {
      const originalId = project.original_project || project.id
      const existing = latestVersions.get(originalId)
      
      if (!existing || project.version > existing.version) {
        latestVersions.set(originalId, project)
      }
    })
    
    return new Page(
      latestVersions.size,
      response.data.next,
      response.data.previous,
      Array.from(latestVersions.values())
    )
  }

  async findById(id: string): Promise<Project> {
    const url = `/projects/${id}`
    const response = await this.request.get(url)
    return toModel(response.data)
  }

  async getProjectDetails(id: string): Promise<Project> {
    const url = `/projects/${id}`
    const response = await this.request.get(url)
    return response.data
  }

  async create(item: Project): Promise<Project> {
    const url = `/projects`
    const payload = toPayload(item)
    const response = await this.request.post(url, payload)
    return toModel(response.data)
  }

  async update(item: Project): Promise<void> {
    const url = `/projects/${item.id}`
    const payload = toPayload(item)
    await this.request.patch(url, payload)
  }

  async bulkDelete(projectIds: number[]): Promise<void> {
    const url = `/projects`
    await this.request.delete(url, { ids: projectIds })
  }

  async clone(project: Project): Promise<Project> {
    const url = `/projects/${project.id}/clone`
    const response = await this.request.post(url)
    return toModel(response.data)
  }

  async getAnnotationStatistics(projectId: string, params: string): Promise<any> {
    const url = `/projects/${projectId}/annotation-statistics?${params}`
    const response = await this.request.get(url)
    return response.data
  }

  async getAnnotationStatisticsWithVersion(projectId: string, params: string): Promise<any> {
    const url = `/projects/${projectId}/all-versions-statistics?${params}`
    const response = await this.request.get(url)
    return response.data
  }

  async getProjectVersions(projectId: string): Promise<Project[]> {
    const url = `/projects/${projectId}/versions`
    const response = await this.request.get(url)
    return response.data.map((item: { [key: string]: any }) => toModel(item))
  }

  async closeProject(projectId: string): Promise<void> {
    const url = `/projects/${projectId}/close`
    await this.request.post(url)
  }

  async reopenProject(projectId: string): Promise<any> {
    const url = `/projects/${projectId}/reopen`
    const response = await this.request.post(url)
    return response
  }

  async listRules(projectId: string, limit: number = 15, offset: number = 0): Promise<Rule[]> {
    const url = `/projects/${projectId}/rules?limit=${limit}&offset=${offset}`
    try {
      const response = await this.request.get(url)
      console.log('Rules response:', response)  // Debug log
      
      if (!response || !response.data) {
        console.warn('No response or data received from rules endpoint')
        return []
      }

      // Handle both array and paginated response formats
      const rulesData = Array.isArray(response.data) ? response.data : 
                       response.data.results ? response.data.results : []
      
      console.log('Rules data to process:', rulesData)  // Debug log
      
      return rulesData.map((rule: any) => {
        console.log('Processing rule:', rule)  // Debug log
        return Rule.create(
          rule.id,
          rule.name,
          rule.description,
          rule.project,
          rule.created_at,
          rule.updated_at,
          rule.upvotes_count,
          rule.downvotes_count,
          rule.vote_percentage,
          rule.user_vote,
          rule.voting_closed,
          rule.version,
          rule.voting_end_date || null,
          rule.voting_end_time || null
        )
      })
    } catch (e) {
      console.error('Error in listRules:', e)
      throw e
    }
  }

  async createRule(projectId: string, name: string, description: string, version: number, votingEndDate?: string, votingEndTime?: string): Promise<Rule> {
    const url = `/projects/${projectId}/rules`
    const data = { 
      name, 
      description,
      project: parseInt(projectId),  // Convert to number as expected by backend
      version,
      voting_end_date: votingEndDate || null,
      voting_end_time: votingEndTime || null
    }
    console.log('Creating rule with data:', data)  // Debug log
    const response = await this.request.post(url, data)
    console.log('Rule created:', response.data)  // Debug log
    return Rule.create(
      response.data.id,
      response.data.name,
      response.data.description,
      response.data.project,
      response.data.created_at,
      response.data.updated_at,
      response.data.upvotes_count,
      response.data.downvotes_count,
      response.data.vote_percentage,
      response.data.user_vote,
      response.data.voting_closed,
      response.data.version,
      response.data.voting_end_date,
      response.data.voting_end_time
    )
  }

  async updateRule(projectId: string, ruleId: number, name: string, description: string): Promise<void> {
    const url = `/projects/${projectId}/rules/${ruleId}`
    await this.request.put(url, { name, description })
  }

  async deleteRule(projectId: string, ruleId: number): Promise<void> {
    const url = `/projects/${projectId}/rules/${ruleId}`
    await this.request.delete(url)
  }

  async voteRule(projectId: number, ruleId: number, vote: boolean): Promise<Rule> {
    try {
      const response = await this.request.post(`/projects/${projectId}/rules/${ruleId}/vote/`, { is_upvote: vote });
      return Rule.create(
        response.data.id,
        response.data.name,
        response.data.description,
        response.data.project,
        response.data.created_at,
        response.data.updated_at,
        response.data.upvotes_count,
        response.data.downvotes_count,
        response.data.vote_percentage,
        response.data.user_vote,
        response.data.voting_closed
      );
    } catch (e) {
      console.error('Error in voteRule:', e);
      throw e; // Propagate the original error
    }
  }

  async closeRuleVote(projectId: number, ruleId: number): Promise<Rule> {
    try {
      const response = await this.request.post(`/projects/${projectId}/rules/${ruleId}/close-vote/`);
      return Rule.create(
        response.data.id,
        response.data.name,
        response.data.description,
        response.data.project,
        response.data.created_at,
        response.data.updated_at,
        response.data.upvotes_count,
        response.data.downvotes_count,
        response.data.vote_percentage,
        response.data.user_vote,
        response.data.voting_closed
      );
    } catch (e) {
      console.error('Error in closeRuleVote:', e);
      throw e; // Propagate the original error
    }
  }

  async reopenRuleVote(projectId: number, ruleId: number, votingEndDate?: string, votingEndTime?: string): Promise<Rule> {
    try {
      const response = await this.request.post(`/projects/${projectId}/rules/${ruleId}/reopen-vote/`, {
        voting_end_date: votingEndDate || null,
        voting_end_time: votingEndTime || null
      });
      return Rule.create(
        response.data.id,
        response.data.name,
        response.data.description,
        response.data.project,
        response.data.created_at,
        response.data.updated_at,
        response.data.upvotes_count,
        response.data.downvotes_count,
        response.data.vote_percentage,
        response.data.user_vote,
        response.data.voting_closed,
        response.data.version,
        response.data.voting_end_date,
        response.data.voting_end_time
      );
    } catch (e) {
      console.error('Error in reopenRuleVote:', e);
      throw e; // Propagate the original error
    }
  }

  async getAnnotationLabelTable(projectId: string): Promise<any> {
    const url = `/projects/${projectId}/annotation-label-table/`
    const response = await this.request.get(url)
    return response.data
  }
}
