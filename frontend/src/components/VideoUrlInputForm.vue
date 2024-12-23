<script setup>
import { Button } from "@/components/ui/button";
import { FormControl, FormField, FormItem } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast/use-toast";
import { ref } from "vue";

const { toast } = useToast();
const emit = defineEmits(["formSubmitted"]);
const videoUrl = ref(null);

async function handleSubmit() {
  try {
    const response = await fetch(`/api/validate-yt-url?url=${videoUrl.value}`);
    const data = await response.json();
    console.log(data);

    if (response.ok) {
      emit("formSubmitted", data); // Emitting formSubmitted event
      toast({
        title: "Yay!",
        description: "🤗 Ee na hua baat...",
      });
    } else {
      toast({
        title: "Oops! Bad URL Provided.",
        description: "🧐 Kuch toh gadbad hai.",
        variant: "destructive",
      });
    }
  } catch (e) {
    toast({
      title: "Error while verifying URL!",
      description: "🥲 Console dekh.",
      variant: "destructive",
    });
    console.error("Error while verifying URL!", e);
  }
}
</script>

<template>
  <section class="w-1/2">
    <form
      class="rounded-xl border bg-card text-card-foreground shadow p-5 mb-5 text-center"
      @submit.prevent="handleSubmit"
    >
      <FormField name="videoUrl">
        <FormItem>
          <FormControl>
            <Input
              v-model="videoUrl"
              required
              type="text"
              placeholder="YouTube Video URL"
              class="text-center"
            />
          </FormControl>
          <Button type="submit">Submit</Button>
        </FormItem>
      </FormField>
    </form>
  </section>
</template>
