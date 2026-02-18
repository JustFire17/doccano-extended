import { PerspectiveDTO, AssociatePerspectiveDTO } from '@/services/application/perspective/perspectiveData'
import { perspectiveItem, PerspectiveData} from '@/domain/models/perspective/perspective'
import ApiService from '@/services/api.service'

function toModel(dto: PerspectiveDTO): perspectiveItem {
  return {
    id: dto.id,
    name: dto.name,
    type: String(dto.type),
    project: dto.project,
    project_name: dto.project_name,
    options: dto.options,
    perspective_project: dto.perspective_project || null,
    values: dto.values || []
  }
}

export class ApiPerspectiveRepository{
  constructor(private readonly request = ApiService) {}

  async list(projectId: string): Promise<perspectiveItem[]> {
    try {
      const url = `/projects/${projectId}/perspectives`
      const response = await this.request.get(url)
      
      // Check if response data and results exist and are valid
      if (!response.data || !response.data.results || !Array.isArray(response.data.results)) {
        console.warn('Perspective API returned unexpected data structure:', response.data)
        return []
      }
      
      return response.data.results.map((item: any) => toModel(item))
    } catch (error) {
      console.error('Error fetching perspectives:', error)
      return []
    }
  }

  async listAll(projectId: string): Promise<any[]> {
    try {
      const url = `/projects/${projectId}/AllPerspectives`
      const response = await this.request.get(url)
      
      if (!response.data || !Array.isArray(response.data)) {
        console.warn('AllPerspectives API returned unexpected data structure:', response.data)
        return []
      }
      
      return response.data
    } catch (error) {
      console.error('Error fetching all perspectives:', error)
      return []
    }
  }

  async create(projectId: string | number, data: perspectiveItem): Promise<perspectiveItem> {
    const url = `/projects/${projectId}/perspectives`
    const response = await this.request.post(url, data)
    return toModel(response.data)
  }

  async createWithItems(projectId: string | number, data: PerspectiveData): Promise<PerspectiveDTO[]> {
    const url = `/projects/${projectId}/perspectives/create-with-items`
    const response = await this.request.post(url, data)
    return response.data.map((item: any) => new PerspectiveDTO(toModel(item)))
  }

  async associate(projectId: number, data: AssociatePerspectiveDTO): Promise<void> {
    const url = `/projects/${projectId}/associate-perspective`
    await this.request.post(url, data)
  }

  async removeAssociation(projectId: number): Promise<void> {
    const url = `/projects/${projectId}/associate-perspective`
    await this.request.delete(url)
  }

  async update(projectId: string | number, perspectiveId: number, 
    data: perspectiveItem): Promise<perspectiveItem> {
    const url = `/projects/${projectId}/perspectives/${perspectiveId}`
    const response = await this.request.put(url, data)
    return toModel(response.data)
  }

  async delete(projectId: string | number, perspectiveId: number): Promise<void> {
    const url = `/projects/${projectId}/perspectives/${perspectiveId}`
    await this.request.delete(url)
  }

  async deletePerspectiveTotal(projectId: string | number, perspectiveId: number): Promise<void> {
    const url = `/projects/${projectId}/perspectives/${perspectiveId}/delete-total`
    await this.request.delete(url)
  }

  async fill(projectId: string | number, data: Record<number, string | number>): Promise<void> {
    const url = `/projects/${projectId}/perspectives/fill`
    await this.request.post(url, data)
  }
  
  async getFilledValues(projectId: string | number): Promise<Record<number, string>> {
    const url = `/projects/${projectId}/perspectives/fill/values`
    const response = await this.request.get(url)

    const result: Record<number, string> = {}
    for (const item of response.data) {
      result[item.perspective] = item.value
    }
    return result
  }

  async getAllFilledValues(projectId: string | number): Promise<Record<number, string[]>> {
    try {
      const url = `/projects/${projectId}/perspectives/fill/all-values`
      const response = await this.request.get(url)
      
      if (!response.data || typeof response.data !== 'object') {
        console.warn('Perspective all-values API returned unexpected data structure:', response.data)
        return {}
      }
      
      return response.data
    } catch (error) {
      console.error('Error fetching all filled perspective values:', error)
      return {}
    }
  }

  async getUsersWithValue(projectId: string | number, perspectiveId: number, value: string): Promise<string[]> {
    const url = `/projects/${projectId}/perspectives/fill/users-with-value`
    const response = await this.request.get(url, {
      params: {
        perspective_id: perspectiveId,
        value
      }
    })
    return response.data
  }
}