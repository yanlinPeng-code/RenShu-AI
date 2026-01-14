import { GoogleGenAI, Chat, Part } from "@google/genai";
import { UserPersona } from "../types/types";

const apiKey = process.env.API_KEY || ''; // Ensure this is set in your environment
const ai = new GoogleGenAI({ apiKey });

// System instruction for the Public (Patient) Persona
const PUBLIC_SYSTEM_INSTRUCTION = `
You are "RenShu AI", a compassionate and knowledgeable medical assistant incorporating Traditional Chinese Medicine (TCM) wisdom with modern medical advice.
Your tone should be calm, empathetic, and professional.
IMPORTANT: You are an AI, not a doctor. Always advise users to see a professional for serious issues.
When replying, try to be concise but warm.
`;

// System instruction for the Professional (Doctor) Persona
const PROFESSIONAL_SYSTEM_INSTRUCTION = `
You are a highly advanced Clinical Decision Support System. 
Your audience is medical doctors. Use precise medical terminology. 
Be structured, analytical, and data-driven.
Provide differential diagnoses, suggested tests, and highlight potential anomalies in reports.
`;

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

  // Thinking Config (Only for models that support it, but we assume UI handles model selection)
  if (options.enableThinking) {
    config.thinkingConfig = { thinkingBudget: 1024 }; // default budget
  }

  // Tools (Search)
  if (options.enableSearch) {
    config.tools = [{ googleSearch: {} }];
  }

  // Construct Content
  const parts: Part[] = [];

  // Add Files
  files.forEach(file => {
    parts.push({
      inlineData: {
        data: file.data,
        mimeType: file.mimeType
      }
    });
  });

  // Add Text
  parts.push({ text: message });

  // Send
  return chat.sendMessage({
    message: parts.length > 1 ? parts : message,
    config: Object.keys(config).length > 0 ? config : undefined
  });
};


// Helper to analyze user input and update persona
export const analyzeUserPersona = async (text: string, currentPersona: UserPersona): Promise<UserPersona> => {
  try {
    const prompt = `
      Act as a dynamic medical scribe and clinical reasoner.
      Your task is to update the Patient Profile based on the User's latest input: "${text}".

      Current Profile:
      ${JSON.stringify(currentPersona)}

      Instructions:
      1. Extract explicit facts (Age, Gender, Medical History).
      2. Update 'Chief Complaint' with the most recent symptoms mentioned.
      3. CRITICAL: Based on the accumulated Chief Complaint and History, INFER the 'Suspected Diagnosis', 'Contraindications' (e.g., spicy food, cold wind), and 'Recommended Treatment' (TCM or general advice).
      4. If a field is unknown and cannot be inferred yet, keep the existing value.
      5. Keep descriptions concise (under 10 words if possible).

      Return ONLY valid JSON matching this structure:
      {
        "age": "string",
        "gender": "string",
        "chiefComplaint": "string",
        "medicalHistory": "string",
        "suspectedDiagnosis": "string",
        "contraindications": "string",
        "recommendedTreatment": "string"
      }
    `;

    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: prompt,
      config: {
        responseMimeType: "application/json"
      }
    });

    const newData = JSON.parse(response.text || "{}");

    // Ensure we merge correctly to avoid losing data if the model returns partials (though prompt asks for full)
    return { ...currentPersona, ...newData };
  } catch (e) {
    console.error("Persona analysis failed", e);
    return currentPersona;
  }
};

// Helper for Medical Report Analysis
export const analyzeMedicalReport = async (text: string, imageData?: string, mimeType?: string): Promise<string> => {
   const parts: Part[] = [];

   if (imageData && mimeType) {
       parts.push({
           inlineData: { data: imageData, mimeType: mimeType }
       });
   }

   const promptText = `
     Analyze the provided medical report (text or image).
     
     Please structure your response as follows:
     1. **Key Findings**: List the main values or observations. Highlight abnormal values in bold.
     2. **Diagnostic Impression**: What do these results suggest?
     3. **TCM Integration**: Suggest a Traditional Chinese Medicine perspective on these findings (e.g., Liver Qi stagnation, Damp-Heat).
     4. **Recommendations**: Suggested next steps or treatments.
     
     Context/Notes from Doctor: ${text || "None provided."}
   `;

   parts.push({ text: promptText });

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
}