<template>
  <div>
    <DiscussionDetail
      :project-id="projectId"
      :discussion-id="discussionId"
    />
  </div>
</template>

<script>
import DiscussionDetail from '~/components/discussion/DiscussionDetail'

export default {
  components: {
    DiscussionDetail
  },
  layout: 'project',
  
  data() {
    return {
      projectId: this.$route.params.id,
      discussionId: this.$route.params.discussionId
    }
  },
  
  head() {
    return {
      title: 'Discussion'
    }
  }
}
</script> 