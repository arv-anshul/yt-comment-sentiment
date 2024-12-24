<script lang="js" setup>
import Button from "@/components/ui/button/Button.vue";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useToast } from "@/components/ui/toast/use-toast";
import { reactive, watchEffect } from "vue";
import { YouTubeIcon } from "vue3-simple-icons";

const props = defineProps({
  videoId: { type: String, require: true },
  class: { type: String, require: false },
});
const { toast } = useToast();
const emit = defineEmits(["submitVideoDetails"]);
const data = reactive({
  videoDetails: null,
  showDetails: false,
});

function formatDuration(duration) {
  const matches = duration.match(
    /P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/
  );
  if (!matches) {
    return "N/A";
  }

  const days = matches[1] ? parseInt(matches[1]) : 0;
  const hours = matches[2] ? parseInt(matches[2]) : 0;
  const minutes = matches[3] ? parseInt(matches[3]) : 0;
  const seconds = matches[4] ? parseInt(matches[4]) : 0;

  let result = "";

  if (days > 0) {
    result += `${days}d `;
  }
  if (hours > 0 || days > 0) {
    result += `${hours}h `;
  }
  if (minutes > 0 || hours > 0 || days > 0) {
    result += `${minutes}m `;
  }
  result += `${seconds}s`;

  return result.trim();
}

function formatPublishedAt(publishedAt) {
  const date = new Date(publishedAt);
  if (isNaN(date)) {
    return "N/A";
  }

  const day = date.getDate().toString().padStart(2, "0");
  const month = date.toLocaleString("en-US", { month: "short" });
  const year = date.getFullYear();
  return `${day} ${month} ${year}`;
}

// Fetches data from API using videoId every time videoId changes
watchEffect(async () => {
  console.log("Fecthing videos details...");
  const response = await fetch(
    `/api/youtube/video-details?video_id=${props.videoId}`,
    {
      headers: {
        "X-API-KEY": import.meta.env.VITE_YOUTUBE_API_KEY,
      },
    }
  );
  const resData = await response.json();

  try {
    console.log("Fecthing videos details got status code:", response.status);
    if (response.ok) {
      data.videoDetails = resData;
      data.showDetails = true;
      emit("submitVideoDetails", resData);

      toast({
        title: "Fetched video details!",
        description: "👀 Check kar sahi hau na.",
      });
      console.log(resData);
    } else {
      toast({
        title: "Error while fetching video details!",
        description: "🔗 " + resData.detail,
        variant: "destructive",
      });
      console.error(resData);
    }
  } catch (e) {
    toast({
      title: "Error while fetching video details!",
      description: "😰 yeh bada lafda hai, console dekh.",
      variant: "destructive",
    });
    console.error("Got error while fetch video details:", e);
  }
});
</script>

<template>
  <Card :class="props.class" v-if="data.showDetails">
    <CardHeader class="text-center">
      <CardTitle class="font-bold">
        {{ data.videoDetails.title }}
      </CardTitle>
      <img
        :src="`https://i.ytimg.com/vi/${data.videoDetails.id}/maxresdefault.jpg`"
        class="rounded-lg m-auto"
      />
      <CardDescription class="text-gray-500">
        By {{ data.videoDetails.channelTitle }}
      </CardDescription>
    </CardHeader>
    <CardContent>
      <p class="flex gap-2 justify-center place-items-center">
        <i class="pi pi-eye" title="View Count"></i>
        {{ data.videoDetails.viewCount }}
        <i class="pi pi-thumbs-up" title="Like Count"></i>
        {{ data.videoDetails.likeCount }}
        <i class="pi pi-comment" title="Comment Count"></i>
        {{ data.videoDetails.commentCount }}
      </p>
      <div class="my-3"></div>
      <p class="flex gap-2 justify-center place-items-center">
        <i class="pi pi-calendar" title="Video Published At"></i>
        {{ formatPublishedAt(data.videoDetails.publishedAt) }}
        <i class="pi pi-clock" title="Video Duration"></i>
        {{ formatDuration(data.videoDetails.duration) }}
      </p>
    </CardContent>
    <CardFooter>
      <Button variant="outline" class="w-full" as-child>
        <a :href="`https://youtu.be/${data.videoDetails.id}`">
          View on <YouTubeIcon class="text-red-600" />
        </a>
      </Button>
    </CardFooter>
  </Card>
</template>
