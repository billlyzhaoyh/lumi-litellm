/**
 * @license
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { v4 as uuidv4 } from 'uuid';

/** Shared utils. */

// ****************************************************************************
// CONSTANTS
// ****************************************************************************

/** LumiDocument version (in case LumiDocument object is updated). */
export const LUMI_DOCUMENT_VERSION = 0;

// ****************************************************************************
// TYPES
// ****************************************************************************

// Simple timestamp interface to replace Firebase Timestamp
export interface UnifiedTimestamp {
  seconds: number;
  nanoseconds: number;
  toDate(): Date;
  toMillis(): number;
}

// Helper function to create a timestamp (replaces Timestamp.now())
function createTimestamp(): UnifiedTimestamp {
  const now = Date.now();
  return {
    seconds: Math.floor(now / 1000),
    nanoseconds: (now % 1000) * 1000000,
    toDate(): Date {
      return new Date(this.seconds * 1000 + this.nanoseconds / 1000000);
    },
    toMillis(): number {
      return this.seconds * 1000 + this.nanoseconds / 1000000;
    },
  };
}

/** Temporary LumiDocument object. */
export interface LumiDocument {
  id: string;
  versionLumi: number; // use LUMI_DOCUMENT_VERSION
  versionArxiv: string; // version from arXiv
  content: string;
  dateCreated: UnifiedTimestamp;
  dateEdited: UnifiedTimestamp;
}

// ****************************************************************************
// FUNCTIONS
// ****************************************************************************

/** Create new LumiDocument. */
export function createLumiDocument(
  config: Partial<LumiDocument> = {}
): LumiDocument {
  return {
    id: config.id ?? generateId(),
    versionLumi: config.versionLumi ?? LUMI_DOCUMENT_VERSION,
    versionArxiv: config.versionArxiv ?? '',
    content: config.content ?? '',
    dateCreated: config.dateCreated ?? createTimestamp(),
    dateEdited: config.dateEdited ?? createTimestamp(),
  };
}

export function generateId(isSequential: boolean = false): string {
  // If isSequential is selected, the ID will be lower in the alphanumeric
  // scale as time progresses. This helps to ensure that IDs created at a later
  // time will be sorted later.
  if (isSequential) {
    const timestamp = Date.now().toString(36);
    const randomPart = Math.random().toString(36).substring(2, 8);
    return `${timestamp}-${randomPart}`;
  }

  return uuidv4();
}

export function debounce<T extends Function>(fn: T, ms = 300): T {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  return function (this: any, ...args: any[]) {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      fn.apply(this, args);
    }, ms);
  } as unknown as T;
}

export function areArraysEqual<T>(arrayA: T[], arrayB: T[]): boolean {
  if (arrayA.length !== arrayB.length) {
    return false;
  }
  for (let i = 0; i < arrayA.length; i++) {
    if (arrayA[i] !== arrayB[i]) {
      return false;
    }
  }
  return true;
}
