import { Discussion, DiscussionMessage } from '~/domain/models/discussion/discussion'
import { APIDiscussionRepository, SearchQuery } from '~/repositories/discussion/apiDiscussionRepository'
import { Page } from '~/domain/models/page'

export interface SearchQueryParams {
  limit: string
  offset: string
  status?: string
  sortBy?: string
  sortDesc?: string
}

export class DiscussionApplicationService {
  constructor(private readonly repository: APIDiscussionRepository) {}

  get SearchQuery(): typeof SearchQuery {
    return SearchQuery
  }

  public async listDiscussions(projectId: string, query: SearchQuery): Promise<Page<Discussion>> {
    try {
      return await this.repository.listDiscussions(projectId, query)
    } catch (e: any) {
      const errorMessage = e.message || 'Error listing discussions'
      throw new Error(errorMessage)
    }
  }

  public async findDiscussionById(projectId: string, discussionId: string): Promise<Discussion> {
    try {
      return await this.repository.findDiscussionById(projectId, discussionId)
    } catch (e: any) {
      const errorMessage = e.message || 'Error finding discussion'
      throw new Error(errorMessage)
    }
  }

  // Alias for backwards compatibility
  public async getDiscussion(projectId: string, discussionId: string): Promise<Discussion> {
    return await this.findDiscussionById(projectId, discussionId)
  }

  public async createDiscussion(projectId: string, discussion: Discussion): Promise<Discussion> {
    try {
      return await this.repository.createDiscussion(projectId, discussion)
    } catch (e: any) {
      const errorMessage = e.message || 'Error creating discussion'
      throw new Error(errorMessage)
    }
  }

  public async updateDiscussion(projectId: string, discussion: Discussion): Promise<Discussion> {
    try {
      return await this.repository.updateDiscussion(projectId, discussion)
    } catch (e: any) {
      const errorMessage = e.message || 'Error updating discussion'
      throw new Error(errorMessage)
    }
  }

  public async deleteDiscussion(projectId: string, discussionId: number): Promise<void> {
    try {
      await this.repository.deleteDiscussion(projectId, discussionId)
    } catch (e: any) {
      const errorMessage = e.message || 'Error deleting discussion'
      throw new Error(errorMessage)
    }
  }

  public async listMessages(projectId: string, discussionId: string): Promise<DiscussionMessage[]> {
    try {
      return await this.repository.listMessages(projectId, discussionId)
    } catch (e: any) {
      const errorMessage = e.message || 'Error listing messages'
      throw new Error(errorMessage)
    }
  }

  // Alias for backwards compatibility
  public async getMessages(projectId: string, discussionId: string): Promise<DiscussionMessage[]> {
    return await this.listMessages(projectId, discussionId)
  }

  public async createMessage(projectId: string, discussionId: string, message: DiscussionMessage): Promise<DiscussionMessage> {
    try {
      return await this.repository.createMessage(projectId, discussionId, message)
    } catch (e: any) {
      const errorMessage = e.message || 'Error creating message'
      throw new Error(errorMessage)
    }
  }

  public async updateMessage(projectId: string, discussionId: string, message: DiscussionMessage): Promise<DiscussionMessage> {
    try {
      return await this.repository.updateMessage(projectId, discussionId, message)
    } catch (e: any) {
      const errorMessage = e.message || 'Error updating message'
      throw new Error(errorMessage)
    }
  }

  public async deleteMessage(projectId: string, discussionId: string, messageId: number): Promise<void> {
    try {
      await this.repository.deleteMessage(projectId, discussionId, messageId)
    } catch (e: any) {
      const errorMessage = e.message || 'Error deleting message'
      throw new Error(errorMessage)
    }
  }
} 