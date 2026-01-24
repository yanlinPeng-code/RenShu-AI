import { GoogleGenAI, Chat, Part } from "@google/genai";
import { UserPersona } from "../types";
import {
  PUBLIC_SYSTEM_INSTRUCTION,
  PROFESSIONAL_SYSTEM_INSTRUCTION,
  PERSONA_ANALYSIS_PROMPT,
  REPORT_ANALYSIS_PROMPT
} from "../constants";

const apiKey = process.env.API_KEY || '';
const ai = new GoogleGenAI({ apiKey });

export const createPublicChat = (modelId: string = 'gemini-3-flash-preview'): Chat => {
  return ai.chats.create({
    model: modelId,
    config: {
      systemInstruction: PUBLIC_SYSTEM_INSTRUCTION,
      temperature: 0.7,
    },
  });
};

export const createProfessionalChat = (modelId: string = 'gemini-3-pro-preview'): Chat => {
  return ai.chats.create({
    model: modelId,
    config: {
      systemInstruction: PROFESSIONAL_SYSTEM_INSTRUCTION,
      temperature: 0.3,
    },
  });
};

export const sendMessageWithConfig = async (
  chat: Chat,
  message: string,
  files: Array<{data: string, mimeType: string}> = [],
  options: { enableThinking: boolean; enableSearch: boolean }
) => {
  const config: any = {};

  if (options.enableThinking) {
    config.thinkingConfig = { thinkingBudget: 1024 };
  }

  if (options.enableSearch) {
    config.tools = [{ googleSearch: {} }];
  }

  const parts: Part[] = [];

  files.forEach(file => {
    parts.push({
      inlineData: {
        data: file.data,
        mimeType: file.mimeType
      }
    });
  });

  parts.push({ text: message });

  return chat.sendMessage({
    message: parts.length > 1 ? parts : message,
    config: Object.keys(config).length > 0 ? config : undefined
  });
};

export const analyzeUserPersona = async (text: string, currentPersona: UserPersona): Promise<UserPersona> => {
  try {
    const prompt = PERSONA_ANALYSIS_PROMPT(text, currentPersona);

    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: prompt,
      config: {
        responseMimeType: "application/json"
      }
    });

    const newData = JSON.parse(response.text || "{}");
    return { ...currentPersona, ...newData };
  } catch (e) {
    console.error("Persona analysis failed", e);
    return currentPersona;
  }
};

export const analyzeMedicalReport = async (text: string, imageData?: string, mimeType?: string): Promise<string> => {
  const parts: Part[] = [];

  if (imageData && mimeType) {
    parts.push({
      inlineData: { data: imageData, mimeType: mimeType }
    });
  }

  parts.push({ text: REPORT_ANALYSIS_PROMPT(text) });

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-pro-preview',
      contents: parts,
    });
    return response.text || "Unable to analyze report. Please ensure the image is clear.";
  } catch (error) {
    console.error("Report analysis failed", error);
    return "System Error: The analysis could not be completed. Please check your API key or connection.";
  }
};
