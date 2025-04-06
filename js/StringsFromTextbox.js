import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

// SimpleCounter.jsを参考にさせてもらいました m(_ _)m
// https://github.com/AonekoSS/ComfyUI-SimpleCounter/blob/main/js/SimpleCounter.js

app.registerExtension({
    name: "StringsFromTextbox",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "StringsFromTextbox" || nodeData.name === "PromptsFromTextbox") {
            const origOnNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;
                const start = this.widgets.find((w) => w.name === "start");
                const mode = this.widgets.find((w) => w.name === "mode");
                const counter = this.widgets.find((w) => w.name === "counter");
                let index = 0;
                counter.type = "converted-widget"; // hidden

                start.serializeValue = () => {
                    if (mode.value === "Continued") {
                        // Continued mode
                        start.value = start.value + 1; 
                    }
                    return start.value;
                }

                counter.serializeValue = () => { 
                    index++;
                    counter.value = index;
                    return index; 
                }
                api.addEventListener("promptQueued", () => { index = 0; }); // reset
                return r;
            }
        }
    }
})
