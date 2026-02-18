import { TagItem } from '~/domain/models/tag/tag'

export const DocumentClassification = 'DocumentClassification'
export const SequenceLabeling = 'SequenceLabeling'
export const Seq2seq = 'Seq2seq'
export const IntentDetectionAndSlotFilling = 'IntentDetectionAndSlotFilling'
export const ImageClassification = 'ImageClassification'
export const ImageCaptioning = 'ImageCaptioning'
export const BoundingBox = 'BoundingBox'
export const Segmentation = 'Segmentation'
export const Speech2text = 'Speech2text'

export const allProjectTypes = <const>[
  DocumentClassification,
  SequenceLabeling,
  Seq2seq,
  IntentDetectionAndSlotFilling,
  ImageClassification,
  ImageCaptioning,
  BoundingBox,
  Segmentation,
  Speech2text
]
export type ProjectType = (typeof allProjectTypes)[number]
const MIN_LENGTH = 1
const MAX_PROJECT_NAME_LENGTH = 100

export const validateMinLength = (text: string): boolean => {
  return text.trim().length >= MIN_LENGTH
}

export const validateNameMaxLength = (name: string): boolean => {
  return name.trim().length <= MAX_PROJECT_NAME_LENGTH
}

export const canDefineCategory = (projectType: ProjectType): boolean => {
  return [
    DocumentClassification,
    IntentDetectionAndSlotFilling,
    ImageClassification,
    BoundingBox,
    Segmentation
  ].includes(projectType)
}

export const canDefineSpan = (projectType: ProjectType): boolean => {
  return [SequenceLabeling, IntentDetectionAndSlotFilling].includes(projectType)
}

export const canDefineLabel = (projectType: ProjectType): boolean => {
  return canDefineCategory(projectType) || canDefineSpan(projectType)
}

export class Project {
  name: string
  description: string
  projectType: ProjectType
  discrepancy_active: boolean
  discrepancy_percentage: number
  closed: boolean
  version: number
  original_project: number | null
  is_current_version: boolean

  constructor(
    readonly id: number,
    readonly _name: string,
    readonly _description: string,
    readonly guideline: string,
    readonly _projectType: string,
    readonly enableRandomOrder: boolean,
    readonly enableSharingMode: boolean,
    readonly exclusiveCategories: boolean,
    readonly allowOverlappingSpans: boolean,
    readonly enableGraphemeMode: boolean,
    readonly useRelation: boolean,
    readonly tags: TagItem[],
    readonly allowMemberToCreateLabelType: boolean = false,
    readonly _discrepancy_active: boolean,
    readonly _discrepancy_percentage: number,
    readonly users: number[] = [],
    readonly createdAt: string = '',
    readonly updatedAt: string = '',
    readonly author: string = '',
    readonly isTextProject: boolean = false,
    readonly perspective_associated: number | null = null,
    readonly _closed: boolean = false,
    readonly _version: number = 1,
    readonly _original_project: number | null = null,
    readonly _is_current_version: boolean = true
  ) {
    if (!validateMinLength(_name)) {
      throw new Error('Project name is required')
    }
    if (!validateNameMaxLength(_name)) {
      throw new Error('Project name must be less than 100 characters')
    }
    if (!validateMinLength(_description)) {
      throw new Error('Project description is required')
    }
    if (!allProjectTypes.includes(_projectType as ProjectType)) {
      throw new Error(`Invalid project type: ${_projectType}`)
    }
    this.name = _name.trim()
    this.description = _description.trim()
    this.projectType = _projectType as ProjectType
    this.discrepancy_active = _discrepancy_active
    this.discrepancy_percentage = _discrepancy_percentage
    this.closed = _closed
    this.version = _version
    this.original_project = _original_project
    this.is_current_version = _is_current_version
  }

  static create(
    id: number,
    name: string,
    description: string,
    guideline: string,
    projectType: string,
    enableRandomOrder: boolean,
    enableSharingMode: boolean,
    exclusiveCategories: boolean,
    allowOverlappingSpans: boolean,
    enableGraphemeMode: boolean,
    useRelation: boolean,
    tags: TagItem[],
    allowMemberToCreateLabelType: boolean,
    discrepancy_active: boolean,
    discrepancy_percentage: number,
    closed: boolean = false,
    version: number = 1,
    original_project: number | null = null,
    is_current_version: boolean = true
  ) {
    return new Project(
      id,
      name,
      description,
      guideline,
      projectType,
      enableRandomOrder,
      enableSharingMode,
      exclusiveCategories,
      allowOverlappingSpans,
      enableGraphemeMode,
      useRelation,
      tags,
      allowMemberToCreateLabelType,
      discrepancy_active,
      discrepancy_percentage,
      [],
      '',
      '',
      '',
      false,
      null,
      closed,
      version,
      original_project,
      is_current_version
    )
  }

  get canDefineLabel(): boolean {
    return canDefineLabel(this.projectType)
  }

  get canDefineCategory(): boolean {
    return canDefineCategory(this.projectType)
  }

  get canDefineSpan(): boolean {
    return canDefineSpan(this.projectType)
  }

  get canDefineRelation(): boolean {
    return this.useRelation
  }

  get taskNames(): string[] {
    if (this.projectType === IntentDetectionAndSlotFilling) {
      return [DocumentClassification, SequenceLabeling]
    }
    return [this.projectType]
  }

  get resourceType(): string {
    if (this.projectType === DocumentClassification) {
      return 'TextClassificationProject'
    }
    return `${this.projectType}Project`
  }

  get isImageProject(): boolean {
    return [ImageClassification, ImageCaptioning, BoundingBox, Segmentation].includes(
      this.projectType
    )
  }

  get isAudioProject(): boolean {
    return [Speech2text].includes(this.projectType)
  }

  get displayVersion(): string {
    return `v${this.version}`
  }
}
