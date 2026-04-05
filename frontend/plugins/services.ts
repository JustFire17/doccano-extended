import { Plugin } from '@nuxt/types'
import { repositories } from './repositories'
import { ExampleApplicationService } from '@/services/application/example/exampleApplicationService'
import { LabelApplicationService } from '@/services/application/label/labelApplicationService'
import { OptionApplicationService } from '@/services/application/option/optionApplicationService'
import { ProjectApplicationService } from '@/services/application/project/projectApplicationService'
import { TagApplicationService } from '@/services/application/tag/tagApplicationService'
import { BoundingBoxApplicationService } from '@/services/application/tasks/boundingBox/boundingBoxApplicationService'
import { SegmentationApplicationService } from '@/services/application/tasks/segmentation/segmentationApplicationService'
import { SequenceLabelingApplicationService } from '@/services/application/tasks/sequenceLabeling/sequenceLabelingApplicationService'
import { PerspectiveApplicationService } from '@/services/application/perspective/perspectiveApplicationService'
import { ManualDiscrepancyApplicationService } from '@/services/application/discrepancy/manualDiscrepancyApplicationService'
import { DiscrepancyService } from '@/services/application/discrepancy/discrepancyService'
import { ReportApplicationService } from '@/services/application/report/reportApplicationService'
import { DiscussionApplicationService } from '@/services/application/discussion/discussionApplicationService'
import { UserApplicationService } from '@/services/application/user/userApplicationService'
import { AnnotationApplicationService } from '@/services/application/annotation/annotationApplicationService'

export interface Services {
  categoryType: LabelApplicationService
  spanType: LabelApplicationService
  relationType: LabelApplicationService 
  project: ProjectApplicationService
  example: ExampleApplicationService
  sequenceLabeling: SequenceLabelingApplicationService
  option: OptionApplicationService
  tag: TagApplicationService
  bbox: BoundingBoxApplicationService
  segmentation: SegmentationApplicationService
  perspective: PerspectiveApplicationService
  manualDiscrepancy: ManualDiscrepancyApplicationService
  discrepancy: DiscrepancyService
  report: ReportApplicationService
  discussion: DiscussionApplicationService
  user: UserApplicationService
  annotation: AnnotationApplicationService
}

declare module 'vue/types/vue' {
  interface Vue {
    readonly $services: Services
  }
}

const plugin: Plugin = (_, inject) => {
  const services: Services = {
    categoryType: new LabelApplicationService(repositories.categoryType),
    spanType: new LabelApplicationService(repositories.spanType),
    relationType: new LabelApplicationService(repositories.relationType),
    project: new ProjectApplicationService(repositories.project),
    example: new ExampleApplicationService(repositories.example),
    sequenceLabeling: new SequenceLabelingApplicationService(
      repositories.span,
      repositories.relation
    ),
    option: new OptionApplicationService(repositories.option),
    tag: new TagApplicationService(repositories.tag),
    bbox: new BoundingBoxApplicationService(repositories.boundingBox),
    segmentation: new SegmentationApplicationService(repositories.segmentation),
    perspective: new PerspectiveApplicationService(repositories.perspective),
    manualDiscrepancy: new ManualDiscrepancyApplicationService(repositories.manualDiscrepancy),
    discrepancy: new DiscrepancyService(require('~/services/api.service').default),
    report: new ReportApplicationService(repositories.report),
    discussion: new DiscussionApplicationService(repositories.discussion),
    user: new UserApplicationService(repositories.user),
    annotation: new AnnotationApplicationService(repositories.annotation)
  }
  inject('services', services)
}

export default plugin
