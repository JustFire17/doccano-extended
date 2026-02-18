import { reactive } from '@nuxtjs/composition-api'
import { Category } from '~/domain/models/tasks/category'

export const useTeacherList = (repository: any) => {
  const state = reactive({
    teacherList: []
  })

  const getTeacherList = async (projectId: string, exampleId: number) => {
    state.teacherList = await repository.list(projectId, exampleId)
  }

  const removeTeacher = async (projectId: string, exampleId: number, teacherId: number) => {
    await repository.delete(projectId, exampleId, teacherId)
    await getTeacherList(projectId, exampleId)
  }

  const checkPerspectives = async (projectId: string) => {
    try {
      const perspectives = await window.$nuxt.$services.perspective.list(projectId)
      
      if (!perspectives || perspectives.length === 0) {
        alert('No perspectives created')
        return false
      }

      const filledValues = await window.$nuxt.$services.perspective.getFilledValues(projectId)
      
      const allFilled = perspectives.every(perspective => {
        const value = filledValues[perspective.id]
        return value !== undefined && value !== ''
      })

      if (!allFilled) {
        alert('You need to fill in all perspectives before you can annotate. You will be redirected to the perspective filling page.')
        window.$nuxt.$router.push(`/projects/${projectId}/perspective/fill`)
        return false
      }

      return true
    } catch (error) {
      console.error('Error checking perspectives:', error)
      return false
    }
  }

  const checkProjectStatus = async (projectId: string) => {
    try {
      const project = await window.$nuxt.$services.project.findById(projectId)
      if (project.closed) {
        alert('Este projeto está fechado. Não é possível fazer anotações.')
        return false
      }
      return true
    } catch (error) {
      console.error('Error checking project status:', error)
      return false
    }
  }

  const annotateLabel = async (projectId: string, exampleId: number, labelId: number) => {
    const canAnnotatePerspectives = await checkPerspectives(projectId)
    const canAnnotateProject = await checkProjectStatus(projectId)
    if (!canAnnotatePerspectives || !canAnnotateProject) return

    const category = Category.create(labelId)
    await repository.create(projectId, exampleId, category)
    await getTeacherList(projectId, exampleId)
  }

  const clearTeacherList = async (projectId: string, exampleId: number) => {
    const canAnnotatePerspectives = await checkPerspectives(projectId)
    const canAnnotateProject = await checkProjectStatus(projectId)
    if (!canAnnotatePerspectives || !canAnnotateProject) return

    await repository.clear(projectId, exampleId)
    await getTeacherList(projectId, exampleId)
  }

  const autoLabel = async (projectId: string, exampleId: number) => {
    const canAnnotatePerspectives = await checkPerspectives(projectId)
    const canAnnotateProject = await checkProjectStatus(projectId)
    if (!canAnnotatePerspectives || !canAnnotateProject) return

    await repository.autoLabel(projectId, exampleId)
    await getTeacherList(projectId, exampleId)
  }

  const annotateOrRemoveLabel = async (projectId: string, exampleId: number, srcKey: string) => {
    const canAnnotatePerspectives = await checkPerspectives(projectId)
    const canAnnotateProject = await checkProjectStatus(projectId)
    if (!canAnnotatePerspectives || !canAnnotateProject) return

    const labelId = parseInt(srcKey, 10)
    // @ts-ignore
    const annotation = state.teacherList.find((item) => item.label === labelId)
    if (annotation) {
      // @ts-ignore
      await removeTeacher(projectId, exampleId, annotation.id)
    } else {
      await annotateLabel(projectId, exampleId, labelId)
    }
  }

  return {
    state,
    getTeacherList,
    annotateLabel,
    annotateOrRemoveLabel,
    removeTeacher,
    clearTeacherList,
    autoLabel
  }
}
