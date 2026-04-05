import { perspectiveItem, PerspectiveData } from '~/domain/models/perspective/perspective'
import { PerspectiveDTO } from '~/services/application/perspective/perspectiveData'

export interface PerspectiveRepository {

  list(projectId: string | number): Promise<perspectiveItem[]>

  listAll(projectId: string | number): Promise<perspectiveItem[]>

  create(projectId: string | number, item: perspectiveItem): Promise<perspectiveItem>

  createWithItems(projectId: string | number, data: PerspectiveData): Promise<PerspectiveDTO[]>

  associate(projectId: number, data: { project_id: number, perspective_project_id: number | null }): Promise<void>
  
  removeAssociation(projectId: number): Promise<void>

  update(projectId: string | number, perspectiveId: number, item: perspectiveItem): Promise<perspectiveItem>

  delete(projectId: string | number, perspectiveId: number): Promise<void>

  deletePerspectiveTotal(projectId: string | number, perspectiveId: number): Promise<void>

  fill(projectId: string | number, data: Record<number, string | number>): Promise<void>
  
  getFilledValues(projectId: string | number): Promise<Record<number, string>>

  getAllFilledValues(projectId: string | number): Promise<Record<number, string[]>>

  getUsersWithValue(projectId: string | number, perspectiveId: number, value: string): Promise<string[]>

}