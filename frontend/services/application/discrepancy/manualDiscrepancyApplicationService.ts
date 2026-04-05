export class ManualDiscrepancyApplicationService {
    private repository: any
  
    constructor(repository: any) {
      this.repository = repository
    }
  
    async submit(projectId: number, payload: {
      example: number,
      description: string,
      label_stats: Array<{
        label_text: string,
        vote_count: number,
        percentage: number
      }>
    }): Promise<void> {
      await this.repository.create(projectId, payload)
    }
  
    async list(projectId: number): Promise<any[]> {
      return await this.repository.list(projectId)
    }
  }