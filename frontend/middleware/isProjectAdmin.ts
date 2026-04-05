import { NuxtAppOptions } from '@nuxt/types'

export default async ({ app, route, redirect }: NuxtAppOptions) => {
  const member = await app.$repositories.member.fetchMyRole(route.params.id)

  if (!member.isProjectAdmin) {
    return redirect(app.localePath('/projects/' + route.params.id))
  }
}
