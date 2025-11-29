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

				// 初期化処理（同期実行）
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

				// 新規作成時（tagsWidgetが空）はデフォルトで prompt を追加
				// ただし、ロード時も最初は空なので、outputsの状態を見て判断する
				if (!tagsWidget.value) {
					// デフォルト出力（Python定義の大量のワイルドカード）かどうかを判定
					// 名前がすべて "*" だったり、型情報を含まない場合はデフォルトとみなす
					const isDefaultOutputs = this.outputs && this.outputs.length > 0 && !this.outputs[0].name.includes("(");

					if (isDefaultOutputs) {
						if (this.outputs) {
							// 全削除
							for (let i = this.outputs.length - 1; i >= 0; i--) {
								this.removeOutput(i);
							}
						}
						// prompt 追加
						const defaultTag = "prompt";
						const defaultType = availableTags[defaultTag];
						this.addOutput(`${defaultTag} (${defaultType})`, defaultType);
						updateTagsWidget(this);
					}
				}

				this.setSize(this.computeSize());

				const onConfigure = this.onConfigure;
				this.onConfigure = function () {
					if (onConfigure) onConfigure.apply(this, arguments);

					// 保存された tagsWidget の値に基づいて出力を同期する
					// 既存の接続（リンク）を維持するため、全削除せずに差分更新を行う
					const tagsWidget = this.widgets ? this.widgets.find(w => w.name === "tags") : null;
					if (tagsWidget && tagsWidget.value) {
						const savedTags = tagsWidget.value.split(",");
						const desiredOutputNames = [];

						// 必要な出力名のリストを作成
						for (const tag of savedTags) {
							const tagName = tag.trim();
							if (!tagName) continue;
							const type = availableTags[tagName] || "STRING";
							desiredOutputNames.push(`${tagName} (${type})`);
						}

						// 1. 不要な出力を削除
						// 後ろからループしてインデックスずれを防ぐ
						if (this.outputs) {
							for (let i = this.outputs.length - 1; i >= 0; i--) {
								const output = this.outputs[i];
								if (!desiredOutputNames.includes(output.name)) {
									this.removeOutput(i);
								}
							}
						}

						// 2. 足りない出力を追加
						// 順序を維持するために、desiredOutputNames の順にチェックして追加したいが、
						// 既存のリンクを壊さずに順序を変えるのは難しい。
						// ここでは「存在しないものだけ末尾に追加」する方針とする。
						for (const outputName of desiredOutputNames) {
							if (this.findOutputSlot(outputName) === -1) {
								const match = outputName.match(/^(.*)\s\((.*)\)$/);
								if (match) {
									const type = match[2];
									this.addOutput(outputName, type);
								}
							}
						}
					}

					this.setSize(this.computeSize());
				};

				return r;
			};
		}
	}
});
