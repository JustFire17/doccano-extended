<template>
  <div>
    <DiscussionList :project-id="projectId" />
  </div>
</template>

<script>
import DiscussionList from '~/components/discussion/DiscussionList'

export default {
  components: {
    DiscussionList
  },
  layout: 'project',
  
  data() {
    return {
      projectId: this.$route.params.id
    }
  },
  
  head() {
    return {
      title: 'Discussions'
    }
  }
}
</script> 