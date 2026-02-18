import { AnnotationItem } from '@/domain/models/report/annotationItem'
import { ReportRepository } from '@/domain/models/report/reportRepository'

export class ReportApplicationService {
  private repository: ReportRepository

  constructor(repository: ReportRepository) {
    this.repository = repository
  }

  public async getAnnotatorReports(
    projectId: string | number,
    filters: {
      dateStart?: string | null,
      dateEnd?: string | null,
      perspectiveId?: string | null,
      perspectiveValue?: string | null,
      exampleId?: string | null,
      username?: string | null,
      projectVersion?: string | null
    }
  ): Promise<AnnotationItem[]> {
    // Mapear os filtros para os parâmetros do repositório
    const params: {
      dateStart?: string | null,
      dateEnd?: string | null,
      perspectiveId?: string | null,
      perspectiveValue?: string | null,
      exampleId?: string | null,
      username?: string | null,
      projectVersion?: string | null
    } = {}

    if (filters.dateStart) {
      params.dateStart = filters.dateStart
    }

    if (filters.dateEnd) {
      params.dateEnd = filters.dateEnd
    }

    if (filters.perspectiveId) {
      params.perspectiveId = filters.perspectiveId
    }

    if (filters.perspectiveValue) {
      params.perspectiveValue = filters.perspectiveValue
    }

    if (filters.exampleId) {
      params.exampleId = filters.exampleId
    }

    if (filters.username) {
      params.username = filters.username
    }

    if (filters.projectVersion) {
      params.projectVersion = filters.projectVersion
    }

    return await this.repository.getAnnotatorReports(projectId, params)
  }
} 