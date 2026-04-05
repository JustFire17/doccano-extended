export class DiscussionMessage {
  constructor(
    public id: number,
    public discussionId: number,
    public sender: number,
    public senderUsername: string,
    public content: string,
    public createdAt: string
  ) {}
}

export interface Annotator {
  id: number
  username: string
  role: string
}

export class Discussion {
  constructor(
    public id: number,
    public projectId: number,
    public name: string,
    public createdBy: number,
    public createdByUsername: string,
    public status: string,
    public createdAt: string,
    public updatedAt: string,
    public messages: DiscussionMessage[] = [],
    public participantsCount: number = 0,
    public projectVersion: number,
    public annotators: Annotator[] = []
  ) {}

  get isOpen(): boolean {
    return this.status === 'open'
  }
} 