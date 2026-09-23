
const MODEL = "gemini-3-flash-preview";

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "no-store"
    }
  });

export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return json({
        status: "VOIDCORE AI ONLINE"
      });
    }

    if (!env.GEMINI_API_KEY) {
      return json({
        error: "AI server is not configured."
      }, 503);
    }

    try {
      const body = await request.json();
      const message = body.message;

      if (
        typeof message !== "string" ||
        !message.trim() ||
        message.length > 4000
      ) {
        return json({
          error: "Invalid message."
        }, 400);
      }

      const history = Array.isArray(body.history)
        ? body.history.slice(-10)
        : [];

      const contents = history
        .filter(item =>
          item &&
          typeof item.content === "string" &&
          item.content.length <= 4000 &&
          ["user", "assistant"].includes(item.role)
        )
        .map(item => ({
          role: item.role === "assistant" ? "model" : "user",
          parts: [{ text: item.content }]
        }));

      if (
        !contents.length ||
        contents[contents.length - 1].role !== "user"
      ) {
        contents.push({
          role: "user",
          parts: [{ text: message }]
        });
      }

      const response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-goog-api-key": env.GEMINI_API_KEY
          },
          body: JSON.stringify({
            contents,
            generationConfig: {
              maxOutputTokens: 1024
            }
          })
        }
      );

      if (!response.ok) {
        return json({
          error: "AI service unavailable.",
          status: response.status
        }, 502);
      }

      const data = await response.json();

      const answer = data.candidates?.[0]?.content?.parts
        ?.filter(part => typeof part.text === "string")
        .map(part => part.text)
        .join("") || "";

      if (!answer) {
        return json({
          error: "No response generated."
        }, 502);
      }

      return json({
        response: answer
      });

    } catch (error) {
      return json({
        error: "Unable to process request."
      }, 500);
    }
  }
};
