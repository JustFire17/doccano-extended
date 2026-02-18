<template>
  <v-app>
    <the-header>
      <template #leftDrawerIcon>
        <v-app-bar-nav-icon @click="drawerLeft = !drawerLeft" />
      </template>
    </the-header>

    <v-navigation-drawer v-model="drawerLeft" app clipped color="">
      <the-side-bar :is-project-admin="isProjectAdmin" :is-annotation-approver="isAnnotationApprover" :project="currentProject" :discrepancy-active="discrepancy_active" />
    </v-navigation-drawer>

    <v-main>
      <v-container fluid fill-height>
        <v-layout justify-center>
          <v-flex fill-height>
            <nuxt />
          </v-flex>
        </v-layout>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { mapGetters } from 'vuex'
import TheHeader from '~/components/layout/TheHeader'
import TheSideBar from '~/components/layout/TheSideBar'

export default {
  components: {
    TheSideBar,
    TheHeader
  },

  data() {
    return {
      drawerLeft: null,
      isProjectAdmin: false,
      isAnnotationApprover: false,
      discrepancy_active: false
    }
  },

  computed: {
    ...mapGetters('projects', ['currentProject'])
  },

  async created() {
      const member = await this.$repositories.member.fetchMyRole(this.$route.params.id)
      console.log('Member role:', member)
      this.isProjectAdmin = member.isProjectAdmin
      this.isAnnotationApprover = member.isAnnotationApprover
      console.log('isProjectAdmin:', this.isProjectAdmin)
      console.log('isAnnotationApprover:', this.isAnnotationApprover)
      const project = await this.$repositories.project.findById(this.$route.params.id)
      console.log('Project:', project)
      this.discrepancy_active = project.discrepancy_active
  }
}
</script>