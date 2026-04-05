import { reactive, useContext } from '@nuxtjs/composition-api'
import _ from 'lodash'
import { ExampleDTO } from '@/services/application/example/exampleData'

export const useExampleItem = () => {
  const state = reactive({
    example: {} as ExampleDTO,
    totalExample: 0,
    progress: {}
  })

  const { app } = useContext()
  const exampleService = app.$services.example

  const getExample = async (
    projectId: string,
    {
      page,
      q,
      isChecked,
      ordering
    }: { page: string; q: string; isChecked: string; ordering: string }
  ) => {
    const examples = await exampleService.fetchOne(projectId, page, q, isChecked, ordering)
    state.totalExample = examples.count
    if (!_.isEmpty(examples) && examples.items.length !== 0) {
      state.example = examples.items[0]
    }
  }

  const getExampleById = async (projectId: string) => {
    state.example = await exampleService.findById(projectId, state.example.id)
  }

  const updateProgress = async (projectId: string) => {
    state.progress = await app.$repositories.metrics.fetchMyProgress(projectId)
  }

  const canConfirm = async (projectId: string): Promise<boolean> => {
    try {
      const member = await app.$repositories.member.fetchMyRole(projectId)
      if (member.isProjectAdmin || member.isAnnotationApprover) {
        return true
      }

      const perspectives = await app.$services.perspective.list(projectId)
      if (!perspectives || perspectives.length === 0) {
        alert('Perspective Not Created')
        return false
      }

      const filledValues = await app.$services.perspective.getFilledValues(projectId)
      const allFilled = perspectives.every((perspective: any) => {
        const value = filledValues[perspective.id]
        return value !== undefined && value !== ''
      })

      if (!allFilled) {
        alert('You need to fill in all perspectives before you can annotate. You will be redirected to the perspective filling page.')
        app.router?.push(`/projects/${projectId}/perspective/fill`)
        return false
      }

      return true
    } catch (error) {
      console.error('Error checking perspectives:', error)
      return false
    }
  }

  const confirm = async (projectId: string) => {
    const allowedToConfirm = await canConfirm(projectId)
    if (!allowedToConfirm) {
      return
    }
    await exampleService.confirm(projectId, state.example.id)
    await getExampleById(projectId)
    updateProgress(projectId)
  }

  return {
    state,
    confirm,
    getExample,
    updateProgress
  }
}
