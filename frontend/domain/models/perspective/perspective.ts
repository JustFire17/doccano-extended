export interface PerspectiveItemData {
  name: string;
  type: string;
  options: string;
}

export interface PerspectiveData {
  name: string;
  items: PerspectiveItemData[];
}

export class perspectiveItem {
  constructor(
    readonly id: number,
    readonly name: string,
    readonly type: string,
    readonly project: number,
    readonly project_name: string,
    readonly options: string,
    readonly perspective_project: number | null = null,
    readonly values: string[] = []
  ) {}

  static create(
    name: string,
    type: string,
    project: number,
    project_name: string,
    options: string = "",
    perspective_project: number | null = null,
    values: string[] = []
  ): perspectiveItem {
    return new perspectiveItem(0, name, type, project, project_name, options, perspective_project, values)
  }
}