<script lang="js" setup>
import { ref, watchEffect } from "vue";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { useToast } from "./ui/toast/use-toast";

const { toast } = useToast();
const props = defineProps({
  sentimentCount: { type: Object, require: true },
  class: { type: String, require: false },
});
const pieChartUrl = ref(null);

watchEffect(async () => {
  try {
    const response = await fetch("/api/sentiment-count-plot", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(props.sentimentCount),
    });

    if (response.ok) {
      const imgBlob = await response.blob();
      pieChartUrl.value = URL.createObjectURL(imgBlob);
      console.log("pieChartUrl.value");
      console.log(pieChartUrl.value);
    } else {
      const error = await response.json();
      toast({
        title: "Error while creating sentiment pie chart!",
        description: "🔗 " + error.detail,
        variant: "destructive",
      });
      console.error(error);
    }
  } catch (e) {
    toast({
      title: "Error while creating sentiment pie chart!",
      description: "😰 yeh bada lafda hai, console dekh.",
      variant: "destructive",
    });
    console.error(e);
  }
});
</script>

<template>
  <Card :class="props.class">
    <CardHeader class="text-center pb-0">
      <CardTitle class="text-2xl">Sentiment Pie Chart</CardTitle>
    </CardHeader>
    <CardContent class="pb-0">
      <img class="max-w-96" :src="pieChartUrl" alt="Sentiment Pie Chart" />
    </CardContent>
    <CardFooter class="flex gap-10 justify-center place-items-center text-lg">
      <div>
        <i
          class="pi pi-comments text-blue-500"
          title="Positive Comments Count"
        ></i>
        {{ props.sentimentCount.positive }}
      </div>
      <div>
        <i class="pi pi-comments" title="Neutral Comments Count"></i>
        {{ props.sentimentCount.neutral }}
      </div>
      <div>
        <i
          class="pi pi-comments text-red-500"
          title="Negative Comments Count"
        ></i>
        {{ props.sentimentCount.negative }}
      </div>
    </CardFooter>
  </Card>
</template>
