import ApiService from '@/services/api.service'

export class ApiManualDiscrepancyRepository {
  constructor(private readonly request = ApiService) {}

  async create(projectId: number, data: any): Promise<void> {
    const url = `/projects/${projectId}/discrepancies/create`
    await this.request.post(url, data)
  }

  async list(projectId: number): Promise<any[]> {
    const url = `/projects/${projectId}/manual-discrepancies`
    const response = await this.request.get(url)
    return response.data
  }
}       