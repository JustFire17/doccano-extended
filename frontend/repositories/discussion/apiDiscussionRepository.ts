import { Page } from '@/domain/models/page'
import { Discussion, DiscussionMessage } from '@/domain/models/discussion/discussion'
import ApiService from '@/services/api.service'

export class SearchQuery {
  readonly limit: number = 10
  readonly offset: number = 0
  readonly status: string = ''
  readonly sortBy: string = 'updatedAt'
  readonly sortDesc: boolean = true

  constructor(_limit: string, _offset: string, _status?: string, _sortBy?: string, _sortDesc?: string) {
    this.limit = /^\d+$/.test(_limit) ? parseInt(_limit) : 10
    this.offset = /^\d+$/.test(_offset) ? parseInt(_offset) : 0
    this.status = _status || ''
    this.sortBy = _sortBy || 'updatedAt'
    this.sortDesc = _sortDesc !== 'false'
  }
}

function toDiscussionModel(item: { [key: string]: any }): Discussion {
  return new Discussion(
    item.id,
    item.project,
    item.name,
    item.created_by,
    item.created_by_username,
    item.status,
    item.created_at,
    item.updated_at,
    item.messages ? item.messages.map((message: { [key: string]: any }) => toMessageModel(message)) : [],
    item.participants_count,
    item.project_version,
    item.annotators || []
  )
}

function toMessageModel(item: { [key: string]: any }): DiscussionMessage {
  return new DiscussionMessage(
    item.id,
    item.discussion,
    item.sender,
    item.sender_username,
    item.content,
    item.created_at
  )
}

function toDiscussionPayload(item: Discussion): { [key: string]: any } {
  return {
    project: item.projectId,
    name: item.name,
    status: item.status,
    created_by: item.createdBy
  }
}

function toMessagePayload(item: DiscussionMessage): { [key: string]: any } {
  return {
    content: item.content,
    sender: item.sender,
    discussion: item.discussionId
  }
}

export class APIDiscussionRepository {
  constructor(private readonly request = ApiService) {}

  async listDiscussions(projectId: string, query: SearchQuery): Promise<Page<Discussion>> {
    const fieldMapper: { [key: string]: string } = {
      updatedAt: 'updated_at',
      createdAt: 'created_at',
      name: 'name'
    }
    const sortBy = fieldMapper[query.sortBy] || 'updated_at'
    const ordering = query.sortDesc ? `-${sortBy}` : `${sortBy}`
    let url = `/projects/${projectId}/discussions?limit=${query.limit}&offset=${query.offset}&ordering=${ordering}`
    if (query.status) {
      url += `&status=${query.status}`
    }
    const response = await this.request.get(url)
    return new Page(
      response.data.count,
      response.data.next,
      response.data.previous,
      response.data.results.map((discussion: { [key: string]: any }) => toDiscussionModel(discussion))
    )
  }

  async findDiscussionById(projectId: string, discussionId: string): Promise<Discussion> {
    const url = `/projects/${projectId}/discussions/${discussionId}`
    const response = await this.request.get(url)
    return toDiscussionModel(response.data)
  }

  async createDiscussion(projectId: string, discussion: Discussion): Promise<Discussion> {
    const url = `/projects/${projectId}/discussions`
    const payload = toDiscussionPayload(discussion)
    const response = await this.request.post(url, payload)
    return toDiscussionModel(response.data)
  }

  async updateDiscussion(projectId: string, discussion: Discussion): Promise<Discussion> {
    const url = `/projects/${projectId}/discussions/${discussion.id}`
    const payload = toDiscussionPayload(discussion)
    const response = await this.request.patch(url, payload)
    return toDiscussionModel(response.data)
  }

  async deleteDiscussion(projectId: string, discussionId: number): Promise<void> {
    const url = `/projects/${projectId}/discussions/${discussionId}`
    await this.request.delete(url)
  }

  async listMessages(projectId: string, discussionId: string): Promise<DiscussionMessage[]> {
    const url = `/projects/${projectId}/discussions/${discussionId}/messages`
    const response = await this.request.get(url)
    return response.data.results.map((message: { [key: string]: any }) => toMessageModel(message))
  }

  async createMessage(projectId: string, discussionId: string, message: DiscussionMessage): Promise<DiscussionMessage> {
    const url = `/projects/${projectId}/discussions/${discussionId}/messages`
    const payload = toMessagePayload(message)
    const response = await this.request.post(url, payload)
    return toMessageModel(response.data)
  }

  async updateMessage(projectId: string, discussionId: string, message: DiscussionMessage): Promise<DiscussionMessage> {
    const url = `/projects/${projectId}/discussions/${discussionId}/messages/${message.id}`
    const payload = toMessagePayload(message)
    const response = await this.request.patch(url, payload)
    return toMessageModel(response.data)
  }

  async deleteMessage(projectId: string, discussionId: string, messageId: number): Promise<void> {
    const url = `/projects/${projectId}/discussions/${discussionId}/messages/${messageId}`
    await this.request.delete(url)
  }
} 