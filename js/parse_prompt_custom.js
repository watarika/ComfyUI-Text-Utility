import { app } from "../../scripts/app.js";

app.registerExtension({
	name: "ComfyUI.TextUtility.ParsePromptCustom",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "ParsePromptCustom") {
			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

				this.serialize_widgets = true;

				// 定義済みタグと型のマッピング
				// NOTE: Keep this in sync with the defaults dictionary in PromptParser.parse() in nodes.py.
				// Any changes to supported tags must be reflected in both files.
				const availableTags = {
					"prompt": "STRING",
					"negative_prompt": "STRING",
					"seed": "INT",
					"steps": "INT",
					"width": "INT",
					"height": "INT",
					"cfg_scale": "FLOAT",
					"batch_size": "INT",
					"outpath_samples": "STRING",
					"outpath_grids": "STRING",
					"prompt_for_display": "STRING",
					"styles": "STRING",
					"sampler_name": "STRING",
					"subseed": "INT",
					"seed_resize_from_h": "INT",
					"seed_resize_from_w": "INT",
					"sampler_index": "INT",
					"n_iter": "INT",
					"subseed_strength": "FLOAT",
					"restore_faces": "BOOLEAN",
					"tiling": "BOOLEAN",
					"do_not_save_samples": "BOOLEAN",
					"do_not_save_grid": "BOOLEAN"
				};

				const tagNames = Object.keys(availableTags);

				// ウィジェット追加
				const comboWidget = this.addWidget("combo", "Tag to Add/Remove", tagNames[0], (v) => { }, { values: tagNames });

				// Add Output Button
				this.addWidget("button", "Add Output", null, () => {
					const selectedTag = comboWidget.value;
					if (!selectedTag) return;

					const type = availableTags[selectedTag];
					const outputName = `${selectedTag} (${type})`;

					// 重複チェック
					const existingIndex = this.findOutputSlot(outputName);
					if (existingIndex !== -1) {
						alert(`Output '${outputName}' already exists.`);
						return;
					}

					// 出力を追加
					this.addOutput(outputName, type);

					updateTagsWidget(this);

					if (this.size[1] < this.computeSize()[1]) {
						this.setSize(this.computeSize());
					}
					app.graph.setDirtyCanvas(true, true);
				});

				// Remove Output Button
				this.addWidget("button", "Remove Output", null, () => {
					const selectedTag = comboWidget.value;
					if (!selectedTag) return;

					const type = availableTags[selectedTag];
					const outputName = `${selectedTag} (${type})`;

					// 存在チェック
					const outputIndex = this.findOutputSlot(outputName);
					if (outputIndex === -1) {
						alert(`Output '${outputName}' does not exist.`);
						return;
					}

					// 出力を削除
					this.removeOutput(outputIndex);

					updateTagsWidget(this);
					this.setSize(this.computeSize());
					app.graph.setDirtyCanvas(true, true);
				});

				// tags widget の更新
				function updateTagsWidget(node) {
					const tagsWidget = node.widgets ? node.widgets.find(w => w.name === "tags") : null;
					if (!tagsWidget) return;

					if (!node.outputs || node.outputs.length === 0) {
						tagsWidget.value = "";
					} else {
						// 出力名から型情報 " (TYPE)" を取り除いてタグ名だけにする
						const tags = node.outputs.map(o => {
							const match = o.name.match(/^(.*)\s\(.*\)$/);
							return match ? match[1] : o.name;
						}).join(",");
						tagsWidget.value = tags;
					}
				}

				// 初期化処理（リトライロジックで堅牢化）
				const initializeNode = (node, retryCount = 0) => {
					const MAX_RETRIES = 10;
					const RETRY_DELAY = 50;

					// tags 保存用ウィジェットを探して隠す
					let tagsWidget = node.widgets ? node.widgets.find(w => w.name === "tags") : null;
					
					if (!tagsWidget && retryCount < MAX_RETRIES) {
						// ウィジェットがまだ準備できていない場合はリトライ
						setTimeout(() => initializeNode(node, retryCount + 1), RETRY_DELAY);
						return;
					}

					if (tagsWidget) {
						tagsWidget.type = "text";
						tagsWidget.computeSize = () => [0, -4];
						tagsWidget.hidden = true;
					} else {
						// なければ作る
						tagsWidget = node.addWidget("text", "tags", "", (v) => { });
						tagsWidget.type = "text";
						tagsWidget.computeSize = () => [0, -4];
						tagsWidget.hidden = true;
					}

					// 新規作成時（tagsWidgetが空）はデフォルトで prompt を追加
					if (!tagsWidget.value) {
						if (node.outputs) {
							// 全削除
							for (let i = node.outputs.length - 1; i >= 0; i--) {
								node.removeOutput(i);
							}
						}
						// prompt 追加
						const defaultTag = "prompt";
						const defaultType = availableTags[defaultTag];
						node.addOutput(`${defaultTag} (${defaultType})`, defaultType);
						updateTagsWidget(node);
					}

					node.setSize(node.computeSize());
				};

				// 初回初期化開始（requestAnimationFrameでより確実なタイミング制御）
				requestAnimationFrame(() => initializeNode(this));

				// onConfigure用の更新処理（リトライロジック付き）
				const updateTagsWithRetry = (node, retryCount = 0) => {
					const MAX_RETRIES = 10;
					const RETRY_DELAY = 50;

					const tagsWidget = node.widgets ? node.widgets.find(w => w.name === "tags") : null;
					if (!tagsWidget && retryCount < MAX_RETRIES) {
						setTimeout(() => updateTagsWithRetry(node, retryCount + 1), RETRY_DELAY);
						return;
					}
					updateTagsWidget(node);
				};

				const onConfigure = this.onConfigure;
				this.onConfigure = function () {
					if (onConfigure) onConfigure.apply(this, arguments);
					requestAnimationFrame(() => updateTagsWithRetry(this));
				};

				return r;
			};
		}
	}
});
