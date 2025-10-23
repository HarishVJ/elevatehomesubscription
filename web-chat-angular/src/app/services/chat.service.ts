import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { ChatMessage } from '../models/product.model';

export type ChatStep = 'appliance_type' | 'brand' | 'model' | 'brand_for_brand' | 'dollar_limit' | 'results';

export interface ChatState {
  step: ChatStep;
  appliance_type: string;
  brand: string;
  model: string;
  brand_for_brand: boolean;
  dollar_limit: number | null;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private messagesSubject = new BehaviorSubject<ChatMessage[]>([]);
  public messages$: Observable<ChatMessage[]> = this.messagesSubject.asObservable();

  private stateSubject = new BehaviorSubject<ChatState>({
    step: 'appliance_type',
    appliance_type: '',
    brand: '',
    model: '',
    brand_for_brand: false,
    dollar_limit: null
  });
  public state$: Observable<ChatState> = this.stateSubject.asObservable();

  constructor() {
    this.addBotMessage('👋 Hello! I\'m your Appliance Research Assistant.');
    this.addBotMessage('I can help you find product specifications and replacement options.');
    this.addBotMessage('Let\'s get started! What type of appliance are you looking for?');
  }

  addBotMessage(content: string): void {
    const messages = this.messagesSubject.value;
    messages.push({
      content,
      isUser: false,
      timestamp: new Date()
    });
    this.messagesSubject.next(messages);
  }

  addUserMessage(content: string): void {
    const messages = this.messagesSubject.value;
    messages.push({
      content,
      isUser: true,
      timestamp: new Date()
    });
    this.messagesSubject.next(messages);
  }

  updateState(updates: Partial<ChatState>): void {
    const currentState = this.stateSubject.value;
    this.stateSubject.next({ ...currentState, ...updates });
  }

  getState(): ChatState {
    return this.stateSubject.value;
  }

  reset(): void {
    this.messagesSubject.next([]);
    this.stateSubject.next({
      step: 'appliance_type',
      appliance_type: '',
      brand: '',
      model: '',
      brand_for_brand: false,
      dollar_limit: null
    });
    this.addBotMessage('👋 Let\'s start a new search!');
    this.addBotMessage('What type of appliance are you looking for?');
  }
}
