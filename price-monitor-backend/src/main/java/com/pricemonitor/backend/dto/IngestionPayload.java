package com.pricemonitor.backend.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.Instant;
import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class IngestionPayload {

    @NotBlank(message = "El nombre del supermercado es obligatorio")
    private String supermarket;

    @NotNull(message = "La fecha de extracción es obligatoria")
    private Instant extractionDate;

    @NotEmpty(message = "La lista de productos no puede estar vacía")
    @Valid
    private List<ProductDto> products;
}
