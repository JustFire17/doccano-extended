import { Page } from '~/domain/models/page'
import { Project } from '~/domain/models/project/project'
import { TagItem } from '~/domain/models/tag/tag'
import { APIProjectRepository, SearchQuery, toModel } from '~/repositories/project/apiProjectRepository'
import { Rule } from '~/domain/models/rule/rule'

type ProjectFields = {
  name: string
  description: string
  guideline: string
  projectType: string
  enableRandomOrder: boolean
  enableSharingMode: boolean
  exclusiveCategories: boolean
  tags: string[]
  allowOverlappingSpans: boolean
  enableGraphemeMode: boolean
  useRelation: boolean
  allowMemberToCreateLabelType: boolean
  discrepancy_active: boolean
  discrepancy_percentage: number
  perspective_associated: number
  closed: boolean
}

export interface SearchQueryData {
  limit: string
  offset: string
  q?: string
  sortBy?: string
  sortDesc?: string
}

export class ProjectApplicationService {
  constructor(private readonly repository: APIProjectRepository) {}

  public async list(q: SearchQueryData): Promise<Page<Project>> {
    try {
      const query = new SearchQuery(q.limit, q.offset, q.q, q.sortBy, q.sortDesc)
      return await this.repository.list(query)
    } catch (e: any) {
      throw new Error(e.response.data.detail)
    }
  }

  public async findById(id: string): Promise<Project> {
    return await this.repository.findById(id)
  }

  public async getProjectDetails(id: string): Promise<Project> {
    return await this.repository.getProjectDetails(id)
  }

  public async create({
    name,
    description,
    projectType,
    enableRandomOrder,
    enableSharingMode,
    exclusiveCategories,
    allowOverlappingSpans,
    enableGraphemeMode,
    useRelation,
    tags,
    guideline = '',
    allowMemberToCreateLabelType = false,
    discrepancy_active = false,
    discrepancy_percentage,
    closed = false
  }: ProjectFields): Promise<Project> {
    console.log('Creating project with the following data:', {
      name,
      description,
      projectType,
      enableRandomOrder,
      enableSharingMode,
      exclusiveCategories,
      allowOverlappingSpans,
      enableGraphemeMode,
      useRelation,
      tags,
      guideline,
      allowMemberToCreateLabelType,
      discrepancy_active,
      discrepancy_percentage
    })
    
    const project = Project.create(
      0,
      name,
      description,
      guideline,
      projectType,
      enableRandomOrder,
      enableSharingMode,
      exclusiveCategories,
      allowOverlappingSpans,
      enableGraphemeMode,
      useRelation,
      tags.map((tag) => TagItem.create(tag)),
      allowMemberToCreateLabelType,
      discrepancy_active,
      discrepancy_percentage,
      closed
    )
    try {
      return await this.repository.create(project)
    } catch (e: any) {
      console.error('Error during project creation:', e.response.data.detail)
      throw new Error(e.response.data.detail)
    }
  }  

  public async update(
    projectId: number,
    {
      name,
      description,
      projectType,
      enableRandomOrder,
      enableSharingMode,
      exclusiveCategories,
      allowOverlappingSpans,
      enableGraphemeMode,
      useRelation,
      guideline = '',
      allowMemberToCreateLabelType,
      discrepancy_active,
      discrepancy_percentage,
      closed
    }: Omit<ProjectFields, 'tags'>
  ): Promise<void> {
    const project = Project.create(
      projectId,
      name,
      description,
      guideline,
      projectType,
      enableRandomOrder,
      enableSharingMode,
      exclusiveCategories,
      allowOverlappingSpans,
      enableGraphemeMode,
      useRelation,
      [],
      allowMemberToCreateLabelType,
      discrepancy_active,
      discrepancy_percentage,
      closed
    )

    try {
      await this.repository.update(project)
    } catch (e: any) {
      throw new Error(e.response.data.detail)
    }
  }

  public bulkDelete(projects: Project[]): Promise<void> {
    const ids = projects.map((project) => project.id)
    return this.repository.bulkDelete(ids)
  }

  public async clone(project: Project): Promise<Project> {
    try {
      return await this.repository.clone(project)
    } catch (e: any) {
      throw new Error(e.response.data.detail)
    }
  }

  async getAnnotationStatistics(projectId: string, params: string): Promise<any> {
    return await this.repository.getAnnotationStatistics(projectId, params)
  }

  async getAnnotationStatisticsWithVersion(projectId: string, params: string): Promise<any> {
    return await this.repository.getAnnotationStatisticsWithVersion(projectId, params)
  }

  async getProjectVersions(projectId: string): Promise<Project[]> {
    return await this.repository.getProjectVersions(projectId)
  }

  async closeProject(projectId: string): Promise<void> {
    return await this.repository.closeProject(projectId)
  }

  async reopenProject(projectId: string): Promise<Project> {
    try {
      const response = await this.repository.reopenProject(projectId)
      return toModel(response.data.new_version)
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || 'Error reopening project')
    }
  }

  async listRules(projectId: string): Promise<Rule[]> {
    try {
      const rules = await this.repository.listRules(projectId)
      console.log('Rules loaded:', rules)  // Debug log
      return rules
    } catch (e: any) {
      console.error('Error loading rules:', e)
      if (e.response?.data?.detail) {
        throw new Error(e.response.data.detail)
      }
      if (e.response?.status === 403) {
        throw new Error('You do not have permission to view rules')
      }
      throw new Error('Failed to load rules')
    }
  }

  async createRule(projectId: string, name: string, description: string, version: number, votingEndDate?: string, votingEndTime?: string): Promise<Rule> {
    try {
      console.log('Creating rule:', { projectId, name, description, version, votingEndDate, votingEndTime })  // Debug log
      const rule = await this.repository.createRule(projectId, name, description, version, votingEndDate, votingEndTime)
      console.log('Rule created:', rule)  // Debug log
      return rule
    } catch (e: any) {
      console.error('Error creating rule:', e)
      throw e
    }
  }

  async updateRule(projectId: string, ruleId: number, name: string, description: string): Promise<void> {
    try {
      console.log('Updating rule:', { projectId, ruleId, name, description })  // Debug log
      await this.repository.updateRule(projectId, ruleId, name, description)
      console.log('Rule updated successfully')  // Debug log
    } catch (e: any) {
      console.error('Error updating rule:', e)
      throw e
    }
  }

  async deleteRule(projectId: string, ruleId: number): Promise<void> {
    try {
      console.log('Deleting rule:', { projectId, ruleId })  // Debug log
      await this.repository.deleteRule(projectId, ruleId)
      console.log('Rule deleted successfully')  // Debug log
    } catch (e: any) {
      console.error('Error deleting rule:', e)
      throw e
    }
  }

  async voteRule(projectId: number, ruleId: number, vote: boolean): Promise<Rule> {
    return await this.repository.voteRule(projectId, ruleId, vote)
  }

  async closeRuleVote(projectId: number, ruleId: number): Promise<Rule> {
    return await this.repository.closeRuleVote(projectId, ruleId)
  }

  async reopenRuleVote(projectId: number, ruleId: number, votingEndDate?: string, votingEndTime?: string): Promise<Rule> {
    return await this.repository.reopenRuleVote(projectId, ruleId, votingEndDate, votingEndTime)
  }

  async getAnnotationLabelTable(projectId: string): Promise<any> {
    return await this.repository.getAnnotationLabelTable(projectId)
  }
}
