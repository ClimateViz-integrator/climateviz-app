import { Message } from "../../models/chatBot/message";

export interface ExtendedMessage extends Message {
  fileData?: {
    blob: Blob;
    filename: string;
    type: 'excel';
  };
}