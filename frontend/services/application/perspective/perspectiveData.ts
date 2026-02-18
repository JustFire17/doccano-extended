import { perspectiveItem } from '~/domain/models/perspective/perspective'

export class PerspectiveDTO {
  id: number
  name: string
  type: string
  project: number
  project_name: string
  options: string
  perspective_project: number | null
  values: string[]

  constructor(item: perspectiveItem) {
    this.id = item.id
    this.name = item.name
    this.type = item.type
    this.project = item.project
    this.project_name = item.project_name
    this.options = item.options
    this.perspective_project = item.perspective_project
    this.values = item.values
  }
}

export interface AssociatePerspectiveDTO {
  project_id: number
  perspective_project_id: number | null
}