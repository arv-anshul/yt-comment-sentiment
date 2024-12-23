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
});
const { toast } = useToast();
const data = reactive({
  videoDetails: null,
  showDetails: false,
});

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
  <section v-if="data.showDetails">
    <Card class="min-w-40 max-w-96">
      <CardHeader class="text-center">
        <CardTitle class="font-bold">
          {{ data.videoDetails.title }}
        </CardTitle>
        <img
          :src="`https://i.ytimg.com/vi/${props.videoId}/maxresdefault.jpg`"
          class="rounded-sm m-auto"
        />
        <CardDescription class="text-gray-500">
          By {{ data.videoDetails.channelTitle }}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <!-- @todo: Add every details in beautiful way -->
        <p>
          <span class="font-bold">Published On:</span>
          {{ data.videoDetails.publishedAt }}
        </p>
        <p>
          <span class="font-bold">Duration:</span>
          {{ data.videoDetails.duration }}
        </p>
      </CardContent>
      <CardFooter>
        <Button variant="outline" class="w-full" as-child>
          <a :href="`https://youtu.be/${props.videoId}`">
            View on <YouTubeIcon class="text-red-600" />
          </a>
        </Button>
      </CardFooter>
    </Card>
  </section>
</template>
