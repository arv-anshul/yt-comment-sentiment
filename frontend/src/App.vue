<script setup>
import { Toaster } from "@/components/ui/toast";
import VideoUrlInputForm from "@/components/VideoUrlInputForm.vue";
import YTVideoDetailsCard from "@/components/YTVideoDetailsCard.vue";
import { ref } from "vue";

const videoIdData = ref(null);
console.log(import.meta.env);
</script>

<template>
  <Toaster></Toaster>
  <div class="m-auto w-3/4 h-[100vh] place-items-center place-content-center">
    <h1 class="text-3xl font-bold text-center mb-5">
      YouTube Comment Sentiment <br />
      <span class="text-red-500 text-base">Analysis Dashboard</span>
    </h1>

    <VideoUrlInputForm @formSubmitted="(data) => (videoIdData = data)" />
    <YTVideoDetailsCard v-if="videoIdData" :videoId="videoIdData.video_id" />
  </div>
</template>
