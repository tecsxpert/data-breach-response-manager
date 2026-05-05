package com.internship.tool.controller;

import com.internship.tool.entity.DataBreach;
import com.internship.tool.service.DataBreachService;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Arrays;
import java.util.Optional;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(BreachController.class)
public class BreachControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private DataBreachService service;

    @Test
    public void testSearch() throws Exception {
        DataBreach breach = new DataBreach();
        breach.setTitle("Test Title");
        
        Mockito.when(service.search("Test")).thenReturn(Arrays.asList(breach));

        mockMvc.perform(get("/api/breaches/search?q=Test"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].title").value("Test Title"));
    }

    @Test
    public void testUpdate() throws Exception {
        UUID id = UUID.randomUUID();
        DataBreach existing = new DataBreach();
        existing.setId(id);
        
        Mockito.when(service.findById(id)).thenReturn(Optional.of(existing));
        Mockito.when(service.save(any())).thenReturn(existing);

        String json = "{\"title\":\"Updated Title\",\"description\":\"Desc\",\"status\":\"Investigating\",\"severity\":\"Low\"}";

        mockMvc.perform(put("/api/breaches/" + id)
                .contentType(MediaType.APPLICATION_JSON)
                .content(json))
                .andExpect(status().isOk());
    }

    @Test
    public void testDelete() throws Exception {
        UUID id = UUID.randomUUID();
        mockMvc.perform(delete("/api/breaches/" + id))
                .andExpect(status().isNoContent());
        Mockito.verify(service).delete(id);
    }
}
