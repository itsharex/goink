export namespace app {
	
	export class ChatInput {
	    session_id: string;
	    novel_id: number;
	    message: string;
	    provider_name: string;
	    model_id: string;
	    reasoning_effort: string;
	
	    static createFrom(source: any = {}) {
	        return new ChatInput(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.session_id = source["session_id"];
	        this.novel_id = source["novel_id"];
	        this.message = source["message"];
	        this.provider_name = source["provider_name"];
	        this.model_id = source["model_id"];
	        this.reasoning_effort = source["reasoning_effort"];
	    }
	}
	export class ChatResult {
	    session_id: string;
	    turn_id: number;
	    final_text: string;
	
	    static createFrom(source: any = {}) {
	        return new ChatResult(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.session_id = source["session_id"];
	        this.turn_id = source["turn_id"];
	        this.final_text = source["final_text"];
	    }
	}
	export class CreateChapterInput {
	    novel_id: number;
	    title: string;
	
	    static createFrom(source: any = {}) {
	        return new CreateChapterInput(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.novel_id = source["novel_id"];
	        this.title = source["title"];
	    }
	}
	export class CreateNovelInput {
	    title: string;
	    description?: string;
	
	    static createFrom(source: any = {}) {
	        return new CreateNovelInput(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.title = source["title"];
	        this.description = source["description"];
	    }
	}
	export class SaveContentInput {
	    novel_id: number;
	    path: string;
	    content: string;
	
	    static createFrom(source: any = {}) {
	        return new SaveContentInput(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.novel_id = source["novel_id"];
	        this.path = source["path"];
	        this.content = source["content"];
	    }
	}
	export class SaveSettingsInput {
	
	
	    static createFrom(source: any = {}) {
	        return new SaveSettingsInput(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	
	    }
	}
	export class SetActiveNovelInput {
	    novel_id: number;
	
	    static createFrom(source: any = {}) {
	        return new SetActiveNovelInput(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.novel_id = source["novel_id"];
	    }
	}

}

export namespace chapter {
	
	export class Chapter {
	    id: number;
	    novel_id: number;
	    chapter_number: number;
	    title: string;
	    summary: string;
	    word_count: number;
	    // Go type: time
	    created_at: any;
	    // Go type: time
	    updated_at: any;
	    file_path: string;
	
	    static createFrom(source: any = {}) {
	        return new Chapter(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.id = source["id"];
	        this.novel_id = source["novel_id"];
	        this.chapter_number = source["chapter_number"];
	        this.title = source["title"];
	        this.summary = source["summary"];
	        this.word_count = source["word_count"];
	        this.created_at = this.convertValues(source["created_at"], null);
	        this.updated_at = this.convertValues(source["updated_at"], null);
	        this.file_path = source["file_path"];
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}

}

export namespace config {
	
	export class AppSettings {
	    ID: number;
	    last_novel_id: number;
	
	    static createFrom(source: any = {}) {
	        return new AppSettings(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.ID = source["ID"];
	        this.last_novel_id = source["last_novel_id"];
	    }
	}

}

export namespace novel {
	
	export class Novel {
	    id: number;
	    title: string;
	    genre: string;
	    description: string;
	    dir_path: string;
	    // Go type: time
	    created_at: any;
	    // Go type: time
	    updated_at: any;
	
	    static createFrom(source: any = {}) {
	        return new Novel(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.id = source["id"];
	        this.title = source["title"];
	        this.genre = source["genre"];
	        this.description = source["description"];
	        this.dir_path = source["dir_path"];
	        this.created_at = this.convertValues(source["created_at"], null);
	        this.updated_at = this.convertValues(source["updated_at"], null);
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}

}

