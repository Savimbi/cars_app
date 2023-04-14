import http from "../http-common";

const upload = (file) => {
//   let formData = new FormData();

//   formData.append("file", file);
//   console.log(formData)

  return http.post("/cars/upload", file, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

const getData = async () => {
    const response = await http.get("/cars");
    console.log(response.data)
  return response.data;
};

export default {
    getData,
    upload,
};