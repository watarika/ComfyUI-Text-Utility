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
				const comboWidget = this.addWidget("combo", "Tag to Add", tagNames[0], (v) => { }, { values: tagNames });

				this.addWidget("button", "Add Output", null, () => {
					const selectedTag = comboWidget.value;
					if (!selectedTag) return;

					const type = availableTags[selectedTag];

					// 出力を追加
					this.addOutput(selectedTag, type);

					updateTagsWidget(this);

					if (this.size[1] < this.computeSize()[1]) {
						this.setSize(this.computeSize());
					}
					app.graph.setDirtyCanvas(true, true);
				});

				this.addWidget("button", "Remove Last Output", null, () => {
					if (this.outputs && this.outputs.length > 0) {
						this.removeOutput(this.outputs.length - 1);
						updateTagsWidget(this);
						this.setSize(this.computeSize());
						app.graph.setDirtyCanvas(true, true);
					}
				});

				// tags widget の更新
				function updateTagsWidget(node) {
					const tagsWidget = node.widgets ? node.widgets.find(w => w.name === "tags") : null;
					if (!tagsWidget) return;

					if (!node.outputs || node.outputs.length === 0) {
						tagsWidget.value = "";
					} else {
						const tags = node.outputs.map(o => o.name).join(",");
						tagsWidget.value = tags;
					}
				}

				// 初期化処理
				setTimeout(() => {
					// tags 保存用ウィジェットを探して隠す
					let tagsWidget = this.widgets ? this.widgets.find(w => w.name === "tags") : null;
					if (tagsWidget) {
						tagsWidget.type = "text";
						tagsWidget.computeSize = () => [0, -4];
						tagsWidget.hidden = true;
					} else {
						// なければ作る
						tagsWidget = this.addWidget("text", "tags", "", (v) => { });
						tagsWidget.type = "text";
						tagsWidget.computeSize = () => [0, -4];
						tagsWidget.hidden = true;
					}

					// 新規作成時（outputsが空の場合）はデフォルトで prompt を追加
					// ただし、ComfyUIはデフォルトで RETURN_TYPES に基づいて出力を作るかもしれない。
					// Python側で RETURN_TYPES = ("*",) * 50 としているので、
					// デフォルトで 50個の出力が作られる可能性がある！？
					// いや、output_node: false なので、デフォルトでは作られない？
					// 通常、ComfyUIは RETURN_TYPES の数だけ出力を作る。

					// なので、onNodeCreated で余分な出力を削除する必要があるかもしれない。
					// あるいは、ロード時は保存された出力が使われるのでOK。
					// 新規作成時だけ、50個の出力を削除して prompt だけにする。

					// tagsWidget が空なら新規作成とみなす
					if (!tagsWidget.value) {
						// 全削除
						if (this.outputs) {
							// 後ろから削除
							for (let i = this.outputs.length - 1; i >= 0; i--) {
								this.removeOutput(i);
							}
						}
						// prompt 追加
						this.addOutput("prompt", "STRING");
						updateTagsWidget(this);
					}

					this.setSize(this.computeSize());
				}, 50);

				// onConfigure はロード時に呼ばれる。
				// ロード時は outputs は保存された状態（ユーザーが追加したもの）になっているはず。
				// なので特に何もしなくていいが、tagsWidget との整合性チェックくらい？
				const onConfigure = this.onConfigure;
				this.onConfigure = function () {
					if (onConfigure) onConfigure.apply(this, arguments);
					setTimeout(() => {
						updateTagsWidget(this);
					}, 50);
				};

				return r;
			};
		}
	}
});
