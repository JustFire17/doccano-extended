import { DiscrepancyItem } from "~/domain/models/discrepancy/discrepancyRepository"

export class DiscrepancyService {
  private request: any

  constructor(axiosInstance: any) {
    this.request = axiosInstance
  }

  // Este método vai ser responsável por buscar as estatísticas das labels de um exemplo específico
  async getLabelStats(projectId: number | string, exampleId: number): Promise<Record<string, { count: number }>> {
    const url = `/projects/${projectId}/examples/${exampleId}/label-stats`  // Confirme que essa URL está correta
    const response = await this.request.get(url)
    return response.data
  }

  // Este método vai ser responsável por enviar a discrepância manual
  async reportManualDiscrepancy(
    projectId: number | string, 
    exampleId: number, 
    description: string, 
    labelStats: { label_text: string, vote_count: number, percentage: number }[]
  ): Promise<void> {
    const url = `/projects/${projectId}/discrepancies/create`
    const payload = {
      example_id: exampleId,
      description,
      label_stats: labelStats // Passa os stats da label
    }
    await this.request.post(url, payload)
  }

  // Método para listar as discrepâncias manuais
  async getManualDiscrepancies(projectId: number | string): Promise<DiscrepancyItem[]> {
    const url = `/projects/${projectId}/discrepancies`
    const response = await this.request.get(url)
    return response.data
  }
}