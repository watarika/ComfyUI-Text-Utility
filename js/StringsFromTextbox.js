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
                const count = this.widgets.find((w) => w.name === "count");
                let counter = 0;
                //count.type = "converted-widget"; // hidden
                count.serializeValue = () => { 
                    counter++;
                    count.value = counter;
                    return start.value + counter; 
                }
                api.addEventListener("promptQueued", () => { counter = 0; }); // reset
                return r;
            }
        }
    }
})
