<script setup>
import SentimentPieChart from "@/components/SentimentPieChart.vue";
import { Toaster } from "@/components/ui/toast";
import VideoComments from "@/components/VideoComments.vue";
import VideoUrlInputForm from "@/components/VideoUrlInputForm.vue";
import YTVideoDetailsCard from "@/components/YTVideoDetailsCard.vue";
import { reactive } from "vue";

const mainData = reactive({
  videoId: null,
  videoDetails: null,
  videoComments: null,
  sentimentCount: null,
});
</script>

<template>
  <Toaster></Toaster>
  <div
    class="m-auto my-5 w-3/4 max-w-5xl place-items-center place-content-center"
  >
    <div class="text-3xl font-bold text-center mb-5">
      <h1 class="">YouTube Comment Sentiment</h1>
      <p class="text-base text-gray-500">
        <span class="text-red-500">Analysis Dashboard</span> |
        <span class="text-blue-500">
          <a
            class="hover:underline font-mono"
            href="https://github.com/arv-anshul"
            title="Go to GitHub Profile"
          >
            @arv-anshul
          </a>
        </span>
      </p>
    </div>

    <VideoUrlInputForm
      @formSubmitted="(data) => (mainData.videoId = data)"
      class="w-3/4 mb-5"
    />

    <div class="flex gap-5 mb-5">
      <YTVideoDetailsCard
        class="max-w-lg"
        v-if="mainData.videoId"
        :videoId="mainData.videoId"
        @submitVideoDetails="(data) => (mainData.videoDetails = data)"
      />
      <SentimentPieChart
        v-if="mainData.sentimentCount"
        :sentimentCount="mainData.sentimentCount"
      />
    </div>

    <VideoComments
      class="min-w-fit w-3/4"
      v-if="mainData.videoId && mainData.videoDetails"
      :videoDetails="mainData.videoDetails"
      @submitVideoComments="(data) => (mainData.videoComments = data)"
      @submitSentimentCount="(data) => (mainData.sentimentCount = data)"
    />
  </div>
</template>
