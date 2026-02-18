import { AnnotationRepository } from '@/domain/models/tasks/annotationRepository'
import { Category } from '@/domain/models/tasks/category'

export class APICategoryRepository extends AnnotationRepository<Category> {
  labelName = 'categories'

  toModel(item: { [key: string]: any }): Category {
    return new Category(item.id, item.label, item.user)
  }

  toPayload(item: Category): { [key: string]: any } {
    return {
      id: item.id,
      label: item.label,
      user: item.user
    }
  }

  public async delete(projectId: string, exampleId: number, labelId: number): Promise<void> {
    try {
      const url = `${this.baseUrl(projectId, exampleId)}/${labelId}`
      await this.request.delete(url)
    } catch (error) {
      if (error.response?.status === 403) {
        alert('Não é possível remover anotações em um projeto fechado.')
      } else if (error.response?.status === 404) {
        // Se a anotação não for encontrada, podemos considerar que já foi removida
        console.log('Anotação já foi removida ou não existe')
      } else {
        alert('Erro ao remover a anotação. Por favor, tente novamente.')
      }
    }
  }
}
