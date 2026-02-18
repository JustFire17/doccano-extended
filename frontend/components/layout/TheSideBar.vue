<template>
  <v-list dense>
    <v-btn color="ms-4 my-1 mb-2 primary text-capitalize" nuxt @click="toLabeling">
      <v-icon left>
        {{ mdiPlayCircleOutline }}
      </v-icon>
      {{ $t('home.startAnnotation') }}
    </v-btn>
    <v-list-item-group v-model="selected" mandatory>
      <v-list-item
        v-for="(item, i) in filteredItems"
        :key="i"
        @click="$router.push(localePath(`/projects/${$route.params.id}/${item.link}`))"
      >
        <v-list-item-action>
          <v-icon>
            {{ item.icon }}
          </v-icon>
        </v-list-item-action>
        <v-list-item-content>
          <v-list-item-title>
            {{ item.text }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list-item-group>
  </v-list>
</template>

<script>
import {
  mdiAccount,
  mdiBookOpenOutline,
  mdiChartBar,
  mdiCog,
  mdiCommentAccountOutline,
  mdiDatabase,
  mdiHome,
  mdiLabel,
  mdiPlayCircleOutline,
  mdiAlertCircleOutline,
  mdiEyeOutline,
  mdiCompare,
  mdiForum,
  mdiGavel,
  mdiNoteText,
  mdiTable
} from '@mdi/js'
import { getLinkToAnnotationPage } from '~/presenter/linkToAnnotationPage'

export default {
  props: {
    isProjectAdmin: {
      type: Boolean,
      default: false,
      required: true
    },
    isAnnotationApprover: {
      type: Boolean,
      default: false,
      required: true
    },
    project: {
      type: Object,
      default: () => ({}),
      required: true
    },
    discrepancyActive: {
      type: Boolean,
      default: false,
      required: true
    }
  },

  data() {
    return {
      selected: 0,
      mdiPlayCircleOutline
    }
  },

  computed: {
    filteredItems() {
      const items = [
        {
          icon: mdiHome,
          text: this.$t('projectHome.home'),
          link: '',
          isVisible: true
        },
        {
          icon: mdiDatabase,
          text: this.$t('dataset.dataset'),
          link: 'dataset',
          isVisible: true
        },
        {
          icon: mdiNoteText,
          text: 'Annotations',
          link: 'annotations',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiLabel,
          text: this.$t('labels.labels'),
          link: 'labels',
          isVisible:
            (this.isProjectAdmin || this.project.allowMemberToCreateLabelType) &&
            this.project.canDefineLabel
        },
        {
          icon: mdiEyeOutline,
          text: this.$t('Perspective'),
          link: 'perspective',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiEyeOutline,
          text: 'Fill Perspectives',
          link: 'perspective/fill',
          isVisible: !this.isProjectAdmin
        },
        {
          icon: mdiEyeOutline,
          text: 'Annotations by Perspective',
          link: 'perspective/annotations',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiLabel,
          text: 'Relations',
          link: 'links',
          isVisible:
            (this.isProjectAdmin || this.project.allowMemberToCreateLabelType) &&
            this.project.canDefineRelation
        },
        {
          icon: mdiAccount,
          text: this.$t('members.members'),
          link: 'members',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiCommentAccountOutline,
          text: 'Comments',
          link: 'comments',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiBookOpenOutline,
          text: this.$t('guideline.guideline'),
          link: 'guideline',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiChartBar,
          text: this.$t('statistics.statistics'),
          link: 'metrics',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiCog,
          text: this.$t('settings.title'),
          link: 'settings',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiAlertCircleOutline,
          text: 'Discrepancies',
          link: 'manual-discrepancies',
          isVisible: (this.isProjectAdmin || this.isAnnotationApprover) && this.project.closed
        },
        {
          icon: mdiAlertCircleOutline,
          text: 'Discrepancies Detection',
          link: 'discrepancies',
          isVisible: this.isProjectAdmin && this.project.closed && this.project.discrepancy_active 
        },
        {
          icon: mdiForum,
          text: 'Discussions',
          link: 'discussions',
          isVisible: true

        },
        {
          icon: mdiCompare,
          text: 'Side-by-Side Annotations',
          link: 'side-by-side',
          isVisible: this.isProjectAdmin
        },        
        {
          icon: mdiChartBar,
          text: 'Annotator Reports',
          link: 'reports/annotators',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiChartBar,
          text: 'Annotation Statistics',
          link: 'reports/StatisticAnnotations',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiChartBar,
          text: 'All-Versions Statistics',
          link: 'reports/AllVersionsStatistics',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiTable,
          text: 'Label Table',
          link: 'reports/AnnotationLabelTable',
          isVisible: this.isProjectAdmin
        },
        {
          icon: mdiGavel,
          text: 'Rules',
          link: 'rules',
          isVisible: this.project.version > 1 || this.project.closed
        }
      ]
      return items.filter((item) => item.isVisible)
    }
  },

  methods: {
    toLabeling() {
      const query = this.$services.option.findOption(this.$route.params.id)
      const link = getLinkToAnnotationPage(this.$route.params.id, this.project.projectType)
      this.$router.push({
        path: this.localePath(link),
        query
      })
    }
  }
}
</script>