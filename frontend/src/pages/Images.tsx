import { Button, Card, Image as AntImage, Upload, message, Space, Popconfirm } from "antd";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";

export default function Images() {
  const { productId } = useParams();
  const pid = Number(productId);
  const [items, setItems] = useState<any[]>([]);

  const load = async () => {
    const res = await api.listImages(pid);
    setItems(res);
  };

  useEffect(() => {
    load();
  }, [productId]);

  return (
    <Card title={`图片管理 #${pid}`}>
      <Upload
        showUploadList={false}
        customRequest={async ({ file, onSuccess, onError }) => {
          try {
            await api.uploadImage(pid, file as File);
            message.success("上传成功");
            await load();
            onSuccess && onSuccess({}, new XMLHttpRequest());
          } catch (e: any) {
            onError && onError(e);
            message.error(e.message || "上传失败");
          }
        }}
      >
        <Button type="primary">上传图片</Button>
      </Upload>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginTop: 12 }}>
        {items.map((img) => (
          <div key={img.id} style={{ border: "1px solid #eee", padding: 8 }}>
            <AntImage
              width={160}
              src={""}
              // fetch presign url once clicked to preview
              preview={{
                visible: false,
              }}
              onClick={async () => {
                const { url } = await api.presign(img.id);
                const w = window.open(url, "_blank");
                if (!w) message.info("请允许弹窗以预览");
              }}
              placeholder={true as any}
            />
            <div style={{ marginTop: 8 }}>{img.image_filename}</div>
            <Space style={{ marginTop: 6 }}>
              <Button size="small" onClick={async () => {
                const { url } = await api.presign(img.id);
                const w = window.open(url, "_blank");
                if (!w) message.info("请允许弹窗以预览");
              }}>预览</Button>
              <Popconfirm title="删除该图片？" onConfirm={async () => { await api.deleteImage(img.id, true); message.success("已删除"); load(); }}>
                <Button size="small" danger>删除</Button>
              </Popconfirm>
            </Space>
          </div>
        ))}
      </div>
    </Card>
  );
}
