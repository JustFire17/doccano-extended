export class Rule {
  constructor(
    readonly id: number,
    readonly name: string,
    readonly description: string,
    readonly project: number,
    readonly createdAt: string,
    readonly updatedAt: string,
    readonly upvotesCount: number = 0,
    readonly downvotesCount: number = 0,
    readonly votePercentage: number = 0,
    readonly userVote: 'upvote' | 'downvote' | null = null,
    readonly votingClosed: boolean = false,
    readonly version: number = 1,
    readonly votingEndDate: string | null = null,
    readonly votingEndTime: string | null = null
  ) {}

  static create(
    id: number,
    name: string,
    description: string,
    project: number,
    createdAt: string,
    updatedAt: string,
    upvotesCount: number = 0,
    downvotesCount: number = 0,
    votePercentage: number = 0,
    userVote: 'upvote' | 'downvote' | null = null,
    votingClosed: boolean = false,
    version: number = 1,
    votingEndDate: string | null = null,
    votingEndTime: string | null = null
  ): Rule {
    return new Rule(
      id,
      name,
      description,
      project,
      createdAt,
      updatedAt,
      upvotesCount,
      downvotesCount,
      votePercentage,
      userVote,
      votingClosed,
      version,
      votingEndDate,
      votingEndTime
    )
  }

  get isVotingEnded(): boolean {
    if (!this.votingEndDate) return false

    const now = new Date()
    const endDate = new Date(this.votingEndDate)
    
    if (this.votingEndTime) {
      const [hours, minutes] = this.votingEndTime.split(':')
      endDate.setHours(parseInt(hours), parseInt(minutes))
    } else {
      endDate.setHours(23, 59, 59)
    }

    return now >= endDate
  }
} 