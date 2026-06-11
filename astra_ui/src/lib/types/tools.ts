/*
 * ASTRA - Automated Smart Telescope Remote Assistant
 * Copyright (C) 2026 Jesus Basallote
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 * 
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

/**
 * Technical types mirroring the Pydantic models defined in the backend.
 * These ensure type safety when handling tool arguments in the frontend.
 */

export interface SearchWikiArgs {
    query: string;
    limit?: number;
}

export interface GetWikiArticleArgs {
    qid: string;
    title?: string;
}

export interface GetWikiSectionArgs extends GetWikiArticleArgs {
    section_index: string;
}

export interface SearchObjectArgs {
    query: string;
}

export interface GetObjectDetailsArgs {
    object_id: string;
    type: 'sidereal' | 'planetary';
}

export interface SlewToArgs {
    id: string;
    name?: string;
    type: 'sidereal' | 'planetary';
    mode: 'TRACK' | 'SLEW' | 'SYNC';
}

export interface FlyToConstellationArgs {
    abbr: string;
    name?: string;
}

export interface FocusObjectArgs {
    id: string;
    name?: string;
    type: 'sidereal' | 'planetary';
}
