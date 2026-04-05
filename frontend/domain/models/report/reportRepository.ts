import { AnnotationItem } from './annotationItem'

export interface ReportRepository {
  getAnnotatorReports(
    projectId: string | number,
    params: {
      dateStart?: string | null,
      dateEnd?: string | null,
      perspectiveId?: string | null,
      perspectiveValue?: string | null,
      exampleId?: string | null,
      username?: string | null,
      projectVersion?: string | null
    }
  ): Promise<AnnotationItem[]>
} 