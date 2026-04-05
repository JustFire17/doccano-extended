import { PerspectiveDTO, AssociatePerspectiveDTO } from './perspectiveData'
import { PerspectiveRepository } from '~/domain/models/perspective/perspectiveRepository'
import { perspectiveItem, PerspectiveData } from '~/domain/models/perspective/perspective'

export class PerspectiveApplicationService {
  private repository: PerspectiveRepository

  constructor(repository: PerspectiveRepository) {
    this.repository = repository
  }

  public async list(projectId: string): Promise<PerspectiveDTO[]> {
    const items = await this.repository.list(projectId)
    return items.map((item) => new PerspectiveDTO(item))
  }

  public async listAll(projectId: string): Promise<any[]> {
    return await this.repository.listAll(projectId)
  }

  async createPerspective(projectId: string | number, 
    data: perspectiveItem): Promise<PerspectiveDTO> {
    const createdItem = await this.repository.create(projectId, data)
    return new PerspectiveDTO(createdItem)
  }

  async createPerspectiveWithItems(projectId: string | number, 
    data: PerspectiveData): Promise<PerspectiveDTO[]> {
    return await this.repository.createWithItems(projectId, data)
  }

  public async associatePerspective(projectId: number, perspectiveProjectId: number): Promise<void> {
    const data: AssociatePerspectiveDTO = {project_id: projectId,perspective_project_id: perspectiveProjectId}
    await this.repository.associate(projectId, data)
  }

  public async removeAssociation(projectId: number): Promise<void> {
    await this.repository.removeAssociation(projectId)
  }

  async updatePerspective(
    projectId: number,
    perspectiveId: number,
    data: perspectiveItem
  ): Promise<PerspectiveDTO> {
    const updatedItem = await this.repository.update(projectId, perspectiveId, data)
    return new PerspectiveDTO(updatedItem)
  }

  async deletePerspective(projectId: string | number, perspectiveId: number): Promise<void> {
    await this.repository.delete(projectId, perspectiveId)
  }

  async deletePerspectiveTotal(projectId: string | number, perspectiveId: number): Promise<void> {
    await this.repository.deletePerspectiveTotal(projectId, perspectiveId)
  }

  async fillPerspectives(projectId: number | string, data: Record<number, string | number>): Promise<void> {
    await this.repository.fill(projectId, data)
  }

  async getFilledValues(projectId: number | string): Promise<Record<number, string>> {
    return await this.repository.getFilledValues(projectId)
  }

  async getAllFilledValues(projectId: number | string): Promise<Record<number, string[]>> {
    return await this.repository.getAllFilledValues(projectId)
  }

  async getUsersWithValue(projectId: number | string, perspectiveId: number, value: string): Promise<string[]> {
    return await this.repository.getUsersWithValue(projectId, perspectiveId, value)
  }
}