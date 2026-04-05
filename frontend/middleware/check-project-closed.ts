import { Context } from '@nuxt/types'

export default async function ({ app, route, redirect, store }: Context) {
  // Skip check for project admins
  const member = await app.$repositories.member.fetchMyRole(route.params.id)
  if (member.isProjectAdmin) {
    return
  }

  // Skip check for non-annotation pages
  const restrictedPages = [
    'text-classification',
    'sequence-labeling',
    'intent-detection-and-slot-filling',
    'segmentation',
    'labels'
  ]
  if (!restrictedPages.includes(route.name?.split('-').pop() || '')) {
    return
  }

  try {
    // Get project from store
    await store.dispatch('projects/setCurrentProject', route.params.id)
    const project = store.getters['projects/currentProject']
    
    // Check if project is closed
    if (project.closed) {
      // Show alert to inform the user
      alert('Este projeto está fechado. Não é possível fazer alterações.')
      
      // Redirect to dataset page if project is closed
      redirect(`/projects/${route.params.id}/dataset`)
    }
  } catch (error) {
    console.error('Error checking project status:', error)
    // In case of error, allow access to prevent blocking the user
  }
} 