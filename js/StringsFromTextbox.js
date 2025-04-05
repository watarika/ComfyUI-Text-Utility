import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

// SimpleCounter.jsを参考にさせてもらいました m(_ _)m
// https://github.com/AonekoSS/ComfyUI-SimpleCounter/blob/main/js/SimpleCounter.js

app.registerExtension({
    name: "StringsFromTextbox",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "StringsFromTextbox") {
            const origOnNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;
                const start = this.widgets.find((w) => w.name === "start");
                const count = this.widgets.find((w) => w.name === "count");
                let counter = start.value;
                count.type = "converted-widget"; // hidden
                count.serializeValue = () => { return counter++; }
                api.addEventListener("promptQueued", () => { counter = start.value; }); // reset
                return r;
            }
        }
    }
})
