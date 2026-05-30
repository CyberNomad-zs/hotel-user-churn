import request from "@/utils/request";

export function downloadFile(url, fileName) {
    return request.get(url, { responseType: 'blob' }).then(blob => {
        const objectUrl = window.URL.createObjectURL(new Blob([blob]));
        const link = document.createElement('a');
        link.href = objectUrl;
        if (fileName) {
            link.download = fileName;
        }
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(objectUrl);
    });
}
