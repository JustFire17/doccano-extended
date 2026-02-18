export interface DiscrepancyItem {
    id: number
    project: number
    example: number
    labelStats: {
      label_text: string
      vote_count: number
      percentage: number
    }[]
    status: 'resolved' | 'unresolved'
    createdAt: string
    updatedAt: string
    createdBy?: string
    description?: string
  }
  
  export interface DiscrepancyRepository {
    create(projectId: number | string, exampleId: number, description: string, labelStats: { label_text: string, vote_count: number, percentage: number }[]): Promise<void>
    list(projectId: number | string): Promise<DiscrepancyItem[]>
  }