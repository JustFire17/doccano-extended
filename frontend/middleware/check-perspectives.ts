import { Context } from '@nuxt/types'
import { perspectiveItem } from '~/domain/models/perspective/perspective'

export default async function ({ app, route, redirect }: Context) {
  // Skip check for non-annotators
  const member = await app.$repositories.member.fetchMyRole(route.params.id)
  if (member.isProjectAdmin || member.isAnnotationApprover) {
    return
  }

  // Skip check for non-annotation pages
  const annotationPages = [
    'text-classification',
    'sequence-labeling',
    'intent-detection-and-slot-filling',
    'segmentation'
  ]
  if (!annotationPages.includes(route.name?.split('-').pop() || '')) {
    return
  }

  try {
    // Get all perspectives for the project
    const perspectives = await app.$services.perspective.list(route.params.id)
    
    // Get filled values for the current user
    const filledValues = await app.$services.perspective.getFilledValues(route.params.id)
    
    // Check if all perspectives are filled
    const allFilled = perspectives.every((perspective: perspectiveItem) => {
      const value = filledValues[perspective.id]
      return value !== undefined && value !== ''
    })

    if (!allFilled) {
      // Show alert to inform the user
      alert('You need to fill out all perspectives before you can annotate. You will be redirected to the perspective filling page.')
      
      // Redirect to fill perspectives page if not all are filled
      redirect(`/projects/${route.params.id}/perspective/fill`)
    }
  } catch (error) {
    console.error('Error checking perspectives:', error)
    // In case of error, allow access to prevent blocking the user
  }
} 