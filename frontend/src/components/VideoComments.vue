<script lang="js" setup>
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ref, watchEffect } from "vue";
import {
  getVideoComments,
  mergeCommentsAndSentiments,
  predictCommentsSentiments,
} from "../lib/youtubeComments.js";

const emit = defineEmits(["submitVideoComments", "submitSentimentCount"]);
const props = defineProps({
  videoDetails: { type: Object, required: true },
  class: { type: String, require: false },
});

const videoComments = ref(null);
const predictedSentiments = ref(null);

watchEffect(async () => {
  videoComments.value = (
    await getVideoComments(props.videoDetails.id)
  ).comments;
  predictedSentiments.value = await predictCommentsSentiments(
    videoComments.value.map(({ textDisplay, publishedAt }) => ({
      text: textDisplay,
      timestamp: publishedAt,
    }))
  );

  videoComments.value = mergeCommentsAndSentiments(
    videoComments.value,
    predictedSentiments.value
  );

  // Sending videoComments to parent
  emit("submitVideoComments", videoComments.value);
  emit("submitSentimentCount", predictedSentiments.value.sentiment_count);
});
</script>

<template>
  <div
    :class="props.class"
    v-if="videoComments"
    class="rounded-xl border bg-card text-card-foreground shadow p-5"
  >
    <Table>
      <TableCaption>
        Comments from
        <a
          class="font-bold hover:text-red-500"
          :href="`https://www.youtube.com/watch?v=${props.videoDetails.id}`"
          >"{{ props.videoDetails.title }}"</a
        >
        by
        <span class="font-bold">{{ props.videoDetails.channelTitle }}</span>
      </TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead class="w-[50px] text-center">Sentiment</TableHead>
          <TableHead>Commentor</TableHead>
          <TableHead>Text</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow
          v-for="(comment, index) in videoComments.slice(0, 20)"
          :key="index"
        >
          <TableCell
            :class="
              comment.sentiment === 1
                ? 'text-blue-500'
                : comment.sentiment === -1
                  ? 'text-red-500'
                  : 'text-gray-700'
            "
            class="text-center"
          >
            <i
              class="pi pi-circle-fill text-lg"
              :title="
                comment.sentiment === 1
                  ? 'Positive Sentiment Comment'
                  : comment.sentiment === -1
                    ? 'Negative Sentiment Comment'
                    : 'Neutral Sentiment Comment'
              "
            ></i>
          </TableCell>
          <TableCell>{{ comment.authorDisplayName }}</TableCell>
          <TableCell>{{ comment.textDisplay }}</TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </div>
</template>
